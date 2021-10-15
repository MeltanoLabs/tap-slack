"""Slack tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_slack.streams import (
    ChannelsStream,
    ChannelMembersStream,
    MessagesStream,
    ThreadsStream,
    UsersStream,
)

STREAM_TYPES = [
    ChannelsStream,
    ChannelMembersStream,
    MessagesStream,
    ThreadsStream,
    UsersStream,
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
        th.Property(
            "auto_join_channels",
            th.BooleanType,
            default=True,
            description="Whether the bot user should attempt to join channels that it has not yet joined. The bot user must be a member of the channel to retrieve messages.",
        ),
        th.Property(
            "thread_lookback_days",
            th.IntegerType,
            default=3,
            description="The number of days to look in the past for new thread replies to existing messages",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
