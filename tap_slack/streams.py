"""Stream type classes for tap-slack."""

from typing import Any, Dict, Optional

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


class ChannelMembersStream(SlackStream):
    name = "channel_members"
    path = "/conversations.members"
    primary_keys = ["channel_id", "id"]
    records_jsonpath = "channels.[*]"
    schema = schemas.channel_members
    parent_stream_type = ChannelsStream
    ignore_parent_replication_keys = True

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["channel"] = context["channel_id"]
        return params


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
        return params


class UsersStream(SlackStream):
    name = "users"
    path = "/users.list"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "members.[*]"
    schema = schemas.users
