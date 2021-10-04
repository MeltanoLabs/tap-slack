"""Slack tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_slack.streams import (
    ChannelsStream,
    ChannelMembersStream,
    MessagesStream,
    FilesStream,
    ThreadsStream,
    UsersStream,
)

STREAM_TYPES = [
    ChannelsStream,
    # ChannelMembersStream,
    # FilesStream,
    MessagesStream,
    ThreadsStream,
    # UsersStream,
]


class TapSlack(Tap):
    """Slack tap class."""

    name = "tap-slack"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the Slack API service",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
