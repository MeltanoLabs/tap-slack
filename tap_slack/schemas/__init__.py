from tap_slack.schemas.channels import schema as channels
from tap_slack.schemas.channel_members import schema as channel_members
from tap_slack.schemas.messages import schema as messages
from tap_slack.schemas.threads import schema as threads
from tap_slack.schemas.users import schema as users

__all__ = [
    "channels",
    "channel_members",
    "messages",
    "threads",
    "users",
]
