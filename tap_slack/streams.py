"""Stream type classes for tap-slack."""

import requests
import pendulum
import time
import copy

from datetime import datetime, timezone, timedelta
from typing import Any, List, Dict, Optional, Iterable, Generator, cast
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk import metrics
from singer_sdk.exceptions import (
    InvalidStreamSortException,
)
from singer_sdk.helpers._state import (
    log_sort_error,
)


from tap_slack.client import SlackStream
from tap_slack import schemas


class ChannelsStream(SlackStream):
    name = "channels"
    path = "/conversations.list"
    primary_keys = ["id"]
    records_jsonpath = "channels.[*]"
    schema = schemas.channels

    def get_child_context(self, record, context):
        """Return context dictionary for child stream."""
        return {"channel_id": record["id"]}

    def get_url_params(self, context, next_page_token):
        """Augment default to filter channel types to return and extract messages from."""
        params = super().get_url_params(context, next_page_token)
        params["exclude_archived"] = False
        params["types"] = ",".join(self.config["channel_types"])
        return params

    def post_process(self, row, context):
        "Join the channel if not a member, but emit no data."
        row = super().post_process(row, context)
        # return all in selected_channels or default to all, exclude any in excluded_channels list
        channel_id = row["id"]
        if self._is_channel_included(channel_id):
            if not row["is_member"] and self.config.get("auto_join_channels", False):
                self._join_channel(channel_id)
            return row

    def _is_channel_included(self, channel_id: str) -> bool:
        selected_channels = self.config.get("selected_channels")
        excluded_channels = self.config.get("excluded_channels", [])
        if channel_id in excluded_channels:
                return False
        if selected_channels and channel_id not in selected_channels:
                return False
        return True

    def _join_channel(self, channel_id: str) -> requests.Response:
        url = f"{self.url_base}/conversations.join"
        params = {"channel": channel_id}
        response = self.requests_session.post(
            url=url, params=params, headers=self.authenticator.auth_headers
        )
        try: 
            if not response.json().get("ok"):
                self.logger.warning(
                    f"Error joining channel: {response.json().get('error')}"
                )
            else:
                self.logger.info("Successfully joined channel: %s", channel_id)
        except Exception as e:
            self.logger.warning(f"An exception was raised while joining channel {channel_id}: {e}. Reponse: {response}")


class ChannelMembersStream(SlackStream):
    name = "channel_members"
    parent_stream_type = ChannelsStream
    path = "/conversations.members"
    primary_keys = ["channel_id", "member_id"]
    records_jsonpath = "members.[*]"
    schema = schemas.channel_members

    ignore_parent_replication_keys = True
    state_partitioning_keys = []

    def parse_response(self, response):
        user_list = extract_jsonpath(self.records_jsonpath, input=response.json())
        yield from ({"member_id": ii} for ii in user_list)

    def post_process(self, row, context=None):
        row = super().post_process(row, context=context)
        row["channel_id"] = context.get("channel_id")
        return row


class MessagesStream(SlackStream):
    name = "messages"
    parent_stream_type = ChannelsStream
    path = "/conversations.history"
    primary_keys = ["channel_id", "ts"]
    replication_key = "ts"
    records_jsonpath = "messages.[*]"
    schema = schemas.messages

    ignore_parent_replication_key = True
    max_requests_per_minute = 45

    @property
    def threads_stream_start(self):
        lookback_days = timedelta(days=self.config["thread_lookback_days"])
        start_date = datetime.now(tz=timezone.utc) - lookback_days
        return start_date.timestamp()
    
    def get_child_context(self, record, context):
        """Return context dictionary for child stream."""
        return {"channel_id": context.get("channel_id"), "record": record}

    def get_url_params(self, context, next_page_token):
        """Augment default to implement incremental syncing."""
        params = super().get_url_params(context, next_page_token)
        start_timestamp = self.get_starting_replication_key_value(context)
        if start_timestamp:
            params["oldest"] = start_timestamp
        return params

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """
        Directly invoke the threads stream sync on relevant messages,
        and filter out messages that have already been synced before.
        """
        threads_stream = self._tap.streams["threads"]
        replication_key_ts = self.get_starting_replication_key_value(context)
        if row.get("thread_ts") and threads_stream.selected:
            threads_context = {**context, **{"thread_ts": row["ts"]}}
            threads_stream.sync(context=threads_context)
            time.sleep(60.0 / threads_stream.max_requests_per_minute)
        if row["ts"] and float(row["ts"]) < replication_key_ts:
            return None
        return row

    def get_starting_replication_key_value(
        self, context: Optional[dict]
    ) -> Optional[int]:
        """
        Threads can continue to have messages for weeks after the original message
        was posted, so we cannot assume that we have scraped all message replies
        at the same time we scrape the original message. This function will return
        the starting timestamp for the EARLIEST of either the regular starting timestamp
        (e.g. for full syncs) or the THREAD_LOOKBACK_DAYS days before the current run.
        A longer THREAD_LOOKBACK_DAYS will result in longer incremental sync runs.
        """
        state = self.get_context_state(context)
        replication_key_value = state.get("replication_key_value")
        if replication_key_value:
            if self.threads_stream_start < float(replication_key_value):
                return self.threads_stream_start
            return float(replication_key_value)
        elif "start_date" in self.config:
            start_date = cast(datetime, pendulum.parse(self.config["start_date"]))
            return start_date.replace(tzinfo=timezone.utc).timestamp()
        else:
            self.logger.info(
                "Setting replication value to 0 to perform full historical sync."
            )
            return 0.0


class MessageReactionsStream(MessagesStream):
    name = "messages-reactions"
    parent_stream_type = MessagesStream
    # This stream does not use an explicit API: it relies on /conversations.history, same as the parent strem
    schema = schemas.reactions

    ignore_parent_replication_key = True
    
    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Return a generator of record-type dictionary objects.

        Overridden function from RESTStream. Make use of the context provided by the
        parent stream, which includes the record -> reactions can be processed from
        this without re-calling the API

        Yields:
            One item per (possibly processed) record in the API.
        """
        if "record" not in context or "record" not in context:
            return
        # As per https://sdk.meltano.com/en/latest/context_object.html, context is not supposed to be
        # mutated... but this object gets stored in the Meltano DB and also gets printed to the console,
        # which are two behaviors we don't want. Singer doesn't seem to have a way to pass "as is" a
        # record from parent to child without the context, so pop
        record = context.pop("record")
        channel_id = context.pop("channel_id")
        context = None
        processed_reactions = self.multi_post_process(record, channel_id)
        for rec in processed_reactions:
            yield rec

    def multi_post_process(self, row: dict, channel_id: str) -> List[dict]:
        """
        Extract only reactions as a separate stream
        """

        reaction_rows = self.extract_reactions_from_msg_record(row, channel_id)
        return reaction_rows

    def extract_reactions_from_msg_record(
        self, row: dict, channel_id: str
    ) -> List[Dict]:
        ret: List[Dict] = []
        if "reactions" not in row:
            return []
        reactions = row["reactions"]
        ts = row.get("ts", "0")
        thread_ts = row.get("thread_ts", "0")
        original_msg_author = row.get("user", "")
        for el in reactions:
            for user in el["users"]:
                reaction_name = el["name"]
                ret.append(
                    {
                        "id": f"react-{ts}-{thread_ts}-{user}-{reaction_name}",
                        "ts": ts,
                        "thread_ts": thread_ts,
                        "original_msg_author": original_msg_author,
                        "channel_id": channel_id,
                        "reaction": reaction_name,
                        "user": user,
                    }
                )
        return ret

    def _sync_records(  # noqa: C901
        self,
        context: dict | None = None,
        *,
        write_messages: bool = True,
    ) -> Generator[dict, Any, Any]:
        """Override Singer SDK's sync to get rid of partitions within the context
        """
        # Initialize metrics
        record_counter = metrics.record_counter(self.name)
        timer = metrics.sync_timer(self.name)

        
        record_index = 0
        context_element: dict | None
        context_list: list[dict] | None
        context_list = [context] if context is not None else self.partitions
        selected = self.selected
        
        with record_counter, timer:
            for context_element in context_list or [{}]:
                record_counter.context = context_element
                timer.context = context_element

                # Small hack: we don't need/want to store parent-specific context, overwrite
                # the context stored within the tap state
                current_context = context_element or None
                default_context = {"default": "default"}
                state = self.get_context_state(default_context)
                state_partition_context = self._get_state_partition_context(
                    default_context,
                )
                self._write_starting_replication_value(default_context)
                child_context: dict = copy.copy(default_context)

                for idx, record_result in enumerate(self.get_records(current_context)):
                    self._check_max_record_limit(current_record_index=record_index)

                    if isinstance(record_result, tuple):
                        # Tuple items should be the record and the child context
                        record, child_context = record_result
                    else:
                        record = record_result
                    try:
                        self._process_record(
                            record,
                            child_context=child_context,
                            partition_context=state_partition_context,
                        )
                    except InvalidStreamSortException as ex:
                        log_sort_error(
                            log_fn=self.logger.error,
                            ex=ex,
                            record_count=record_index + 1,
                            partition_record_count=idx + 1,
                            current_context=current_context,
                            state_partition_context={"default": "default"},
                            stream_name=self.name,
                        )
                        raise ex

                    if selected:
                        if write_messages:
                            self._write_record_message(record)

                        self._increment_stream_state(record, context=current_context)
                        if (
                            record_index + 1
                        ) % self.STATE_MSG_FREQUENCY == 0 and write_messages:
                            self._write_state_message()

                        record_counter.increment()
                        yield record

                    record_index += 1

                if current_context == state_partition_context:
                    # Finalize per-partition state only if 1:1 with context
                    self._finalize_state(state)

        if not context:
            # Finalize total stream only if we have the full context.
            # Otherwise will be finalized by tap at end of sync.
            self._finalize_state(self.stream_state)

        if write_messages:
            # Write final state message if we haven't already
            self._write_state_message()


    @property
    def partitions(self) -> list[dict] | None:
        """
        Intentionally ignore partitions for this stream: no need to maintain bookmarks for every
        single message a reaction refers to
        """
        return None


class ThreadsStream(SlackStream):
    """
    The threads stream is directly invoked by the Messages stream, but not via
    standard parent-child relationship. Instead, parsed messages that have a
    more recent "last_reply_at" timestamp will have a FULL_TABLE sync performed.
    """

    name = "threads"
    path = "/conversations.replies"
    primary_keys = ["channel_id", "thread_ts", "ts"]
    records_jsonpath = "messages.[*]"
    max_requests_per_minute = 45
    schema = schemas.threads

    state_partitioning_keys = []

    def post_process(self, row, context=None):
        row = super().post_process(row, context=context)
        row["channel_id"] = context.get("channel_id")
        return row

    def get_child_context(self, record, context):
        """Return context dictionary for child stream."""
        return {"channel_id": context.get("channel_id"), "record": record}


class ThreadReactionsStream(ThreadsStream):
    name = "threads-reactions"
    parent_stream_type = ThreadsStream
    # This stream does not use an explicit API: it relies on /conversations.history, same as the parent strem
    schema = schemas.reactions

    ignore_parent_replication_key = True

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Return a generator of record-type dictionary objects.

        Overridden function from RESTStream. Make use of the context provided by the
        parent stream, which includes the record -> reactions can be processed from
        this without re-calling the API

        Yields:
            One item per (possibly processed) record in the API.
        """
        # See comment in MessageReactionsStream.get_records
        record = context.pop("record")
        channel_id = context.pop("channel_id")
        context = None
        processed_reactions = self.multi_post_process(record, channel_id)
        for rec in processed_reactions:
            yield rec

    def multi_post_process(self, row: dict, channel_id: str) -> List[dict]:
        """
        Extract only reactions as a separate stream
        """

        reaction_rows = self.extract_reactions_from_msg_record(row, channel_id)
        return reaction_rows

    def extract_reactions_from_msg_record(
        self, row: dict, channel_id: str
    ) -> List[Dict]:
        ret: List[Dict] = []
        if "reactions" not in row:
            return []
        reactions = row["reactions"]
        ts = row.get("ts", "0")
        thread_ts = row.get("thread_ts", "0")
        original_msg_author = row.get("user", "")
        for el in reactions:
            for user in el["users"]:
                reaction_name = el["name"]
                ret.append(
                    {
                        "id": f"react-{ts}-{thread_ts}-{user}-{reaction_name}",
                        "ts": ts,
                        "thread_ts": thread_ts,
                        "original_msg_author": original_msg_author,
                        "channel_id": channel_id,
                        "reaction": reaction_name,
                        "user": user,
                    }
                )
        return ret

    def _sync_records(  # noqa: C901
        self,
        context: dict | None = None,
        *,
        write_messages: bool = True,
    ) -> Generator[dict, Any, Any]:
        """Override Singer SDK's sync to get rid of partitions within the context
        """
        # Initialize metrics
        record_counter = metrics.record_counter(self.name)
        timer = metrics.sync_timer(self.name)

        
        record_index = 0
        context_element: dict | None
        context_list: list[dict] | None
        context_list = [context] if context is not None else self.partitions
        selected = self.selected
        
        with record_counter, timer:
            for context_element in context_list or [{}]:
                record_counter.context = context_element
                timer.context = context_element

                # Small hack: we don't need/want to store parent-specific context, overwrite
                # the context stored within the tap state
                current_context = context_element or None
                default_context = {"default": "default"}
                state = self.get_context_state(default_context)
                state_partition_context = self._get_state_partition_context(
                    default_context,
                )
                self._write_starting_replication_value(default_context)
                child_context: dict = copy.copy(default_context)

                for idx, record_result in enumerate(self.get_records(current_context)):
                    self._check_max_record_limit(current_record_index=record_index)

                    if isinstance(record_result, tuple):
                        # Tuple items should be the record and the child context
                        record, child_context = record_result
                    else:
                        record = record_result
                    try:
                        self._process_record(
                            record,
                            child_context=child_context,
                            partition_context=state_partition_context,
                        )
                    except InvalidStreamSortException as ex:
                        log_sort_error(
                            log_fn=self.logger.error,
                            ex=ex,
                            record_count=record_index + 1,
                            partition_record_count=idx + 1,
                            current_context=current_context,
                            state_partition_context={"default": "default"},
                            stream_name=self.name,
                        )
                        raise ex

                    if selected:
                        if write_messages:
                            self._write_record_message(record)

                        self._increment_stream_state(record, context=current_context)
                        if (
                            record_index + 1
                        ) % self.STATE_MSG_FREQUENCY == 0 and write_messages:
                            self._write_state_message()

                        record_counter.increment()
                        yield record

                    record_index += 1

                if current_context == state_partition_context:
                    # Finalize per-partition state only if 1:1 with context
                    self._finalize_state(state)

        if not context:
            # Finalize total stream only if we have the full context.
            # Otherwise will be finalized by tap at end of sync.
            self._finalize_state(self.stream_state)

        if write_messages:
            # Write final state message if we haven't already
            self._write_state_message()


    @property
    def partitions(self) -> list[dict] | None:
        """
        Intentionally ignore partitions for this stream: no need to maintain bookmarks for every
        single message a reaction refers to
        """
        return None


class UsersStream(SlackStream):
    name = "users"
    path = "/users.list"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "members.[*]"
    schema = schemas.users
