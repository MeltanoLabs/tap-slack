from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("channel_id", th.StringType, required=True),
    th.Property("ts", th.DateTimeType, required=True),
    th.Property(
        "blocks",
        th.ArrayType(
            th.ObjectType(
                th.Property("type", th.StringType),
            )
        ),
    ),
    th.Property("bot_id", th.StringType),
    th.Property(
        "bot_profile",
        th.ObjectType(
            th.Property("app_id", th.StringType),
            th.Property("deleted", th.BooleanType),
            th.Property("id", th.StringType),
            th.Property("name", th.StringType),
            th.Property("team_id", th.StringType),
            th.Property("updated", th.StringType),
        ),
    ),
    th.Property("client_msg_id", th.StringType),
    th.Property("display_as_bot", th.BooleanType),
    th.Property("file_id", th.StringType),
    th.Property("file_ids", th.ArrayType(th.StringType)),
    th.Property(
        "icons",
        th.ObjectType(
            th.Property("emoji", th.StringType),
        ),
    ),
    th.Property("inviter", th.StringType),
    th.Property("is_delayed_message", th.BooleanType),
    th.Property("is_intro", th.BooleanType),
    th.Property("is_locked", th.BooleanType),
    th.Property("is_starred", th.BooleanType),
    th.Property("last_read", th.StringType),
    th.Property("latest_reply", th.StringType),
    th.Property("name", th.StringType),
    th.Property("old_name", th.StringType),
    th.Property("parent_user_id", th.StringType),
    th.Property("permalink", th.StringType),
    th.Property("pinned_to", th.ArrayType(th.StringType)),
    th.Property("purpose", th.StringType),
    th.Property(
        "reactions",
        th.ArrayType(
            th.ObjectType(
                th.Property("count", th.IntegerType),
                th.Property("name", th.StringType),
                th.Property("users", th.ArrayType(th.StringType)),
            )
        ),
    ),
    th.Property("reply_count", th.IntegerType),
    th.Property("reply_users", th.ArrayType(th.StringType)),
    th.Property("reply_users_count", th.IntegerType),
    th.Property("source_team", th.StringType),
    th.Property("subscribed", th.BooleanType),
    th.Property("subtype", th.StringType),
    th.Property("team", th.StringType),
    th.Property("text", th.StringType),
    th.Property("thread_ts", th.StringType),
    th.Property("topic", th.StringType),
    th.Property("type", th.StringType),
    th.Property("unread_count", th.IntegerType),
    th.Property("upload", th.BooleanType),
    th.Property("user", th.StringType),
    th.Property("user_team", th.StringType),
    th.Property("username", th.StringType),
).to_dict()
