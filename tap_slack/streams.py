"""Stream type classes for tap-slack."""

import requests

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Iterable
from singer_sdk.helpers.jsonpath import extract_jsonpath

from tap_slack.client import SlackStream
from tap_slack import schemas


class ChannelsStream(SlackStream):
    name = "channels"
    path = "/conversations.list"
    primary_keys = ["id"]
    records_jsonpath = "channels.[*]"
    schema = schemas.channels

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Override default to return context dictionary for child streams."""
        return {"channel_id": record["id"]}

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["exclude_archived"] = True
        params["include_shared"] = True
        params[
            "types"
        ] = "public_channel"  # may also be 'private_channel', 'mpim', 'im'
        return params


class ChannelMembersStream(SlackStream):
    name = "channel_members"
    parent_stream_type = ChannelsStream
    path = "/conversations.members"
    primary_keys = ["channel_id", "id"]
    records_jsonpath = "members.[*]"
    schema = schemas.channel_members

    ignore_parent_replication_keys = True

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        user_list = extract_jsonpath(self.records_jsonpath, input=response.json())
        return [{"user_id": ii} for ii in user_list]


class MessagesStream(SlackStream):
    name = "messages"
    parent_stream_type = ChannelsStream
    path = "/conversations.history"
    primary_keys = ["channel_id", "ts"]
    replication_key = "ts"
    records_jsonpath = "messages.[*]"
    schema = schemas.messages

    ignore_parent_replication_key = True
    max_requests_per_minute = 50

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        start_time = self.get_starting_timestamp(context)
        if start_time:
            params["oldest"] = start_time.strftime("%s")
        if context.get("channel_id"):
            params["channel"] = context["channel_id"]
        return params


class ThreadsStream(SlackStream):
    name = "threads"
    path = "/conversations.replies"
    primary_keys = ["channel_id", "message_ts", "ts"]
    replication_key = "ts"
    records_jsonpath = "messages.[*]"
    parent_stream_type = ChannelsStream
    ignore_parent_replication_key = True
    max_requests_per_minute = 50
    schema = schemas.threads

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        start_time = self.get_starting_timestamp(context)
        if start_time:
            params["oldest"] = start_time.strftime("%s")
        if context.get("channel_id"):
            params["channel"] = context["channel_id"]
        return params

    def get_starting_timestamp(self, context: Optional[dict]) -> Optional[datetime]:
        """
        Threads can continue to have messages for weeks after the original message
        was posted, so we cannot assume that we have scraped all message replies
        at the same time we scrape the original message. This function will return
        the starting timestamp for the EARLIEST of either the regular starting timestamp
        (e.g. for full syncs) or the THREAD_LOOKBACK_DAYS days before the current run.
        A longer THREAD_LOOKBACK_DAYS will result in longer incremental sync runs.
        """
        stream_start_time = super().get_starting_timestamp(context)
        lookback_start_time = datetime.now(tz=timezone.utc) - timedelta(
            self.config["thread_lookback_days"]
        )
        if lookback_start_time < stream_start_time:
            return lookback_start_time
        return stream_start_time


class UsersStream(SlackStream):
    name = "users"
    path = "/users.list"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "members.[*]"
    schema = schemas.users
