"""Stream type classes for tap-slack."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th

from tap_slack.client import SlackStream
from tap_slack import schemas


class ChannelsStream(SlackStream):
    name = "channels"
    path = "/conversations.list"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "channels.[*]"
    schema = schemas.channels.schema

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {"channel_id": record["id"]}


class ChannelMembersStream(SlackStream):
    name = "channel_members"
    path = "/conversations.members"
    primary_keys = ["channel_id", "id"]
    replication_key = None
    records_jsonpath = "channels.[*]"
    schema = schemas.channel_members.schema
    parent_stream_type = ChannelsStream
    ignore_parent_replication_keys = True

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["channel"] = context["channel_id"]
        return params


class FilesStream(SlackStream):
    name = "files"
    path = "/files.list"
    primary_keys = ["id"]
    replication_key = "ts_from"
    records_jsonpath = "files.[*]"
    schema = schemas.files.schema


class MessagesStream(SlackStream):
    name = "messages"
    path = "/conversations.history"
    primary_keys = ["channel_id", "ts"]
    replication_key = "ts"
    records_jsonpath = "messages.[*]"
    parent_stream_type = ChannelsStream
    ignore_parent_replication_key = True
    max_requests_per_minute = 60
    schema = schemas.messages.schema

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["oldest"] = self.get_starting_replication_key_value(context)
        return params


class ThreadsStream(SlackStream):
    name = "threads"
    path = "/conversations.replies"
    primary_keys = ["channel_id", "message_ts", "ts"]
    replication_key = "ts"
    records_jsonpath = "messages.[*]"
    parent_stream_type = ChannelsStream
    ignore_parent_replication_key = True
    max_requests_per_minute = 60
    schema = schemas.threads.schema

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["oldest"] = self.get_starting_replication_key_value(context)
        # .strftime('%s')
        return params


class UsersStream(SlackStream):
    name = "users"
    path = "/users.list"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "members.[*]"
    schema = schemas.users.schema

