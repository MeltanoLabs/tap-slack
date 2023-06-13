from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("channel_id", th.StringType, required=True),
    th.Property(
        "thread_ts",
        th.StringType,
        required=True,
        description="Epoch timestamp of when the thread parent message was posted.",
    ),
    th.Property(
        "ts",
        th.StringType,
        required=True,
        description="Epoch timestamp of when the thread reply was posted.",
    ),
    th.Property("client_msg_id", th.StringType),
    th.Property("type", th.StringType),
    th.Property("text", th.StringType),
    th.Property("user", th.StringType),
    th.Property("team", th.StringType),
    th.Property("edited", th.StringType),
    th.Property("files", th.StringType),
    th.Property("upload", th.StringType),
    th.Property("parent_user_id", th.StringType),
    th.Property("display_as_bot", th.StringType),
    th.Property("upload", th.StringType),
    th.Property("edited", th.StringType),
    th.Property("is_locked", th.BooleanType),
    th.Property("files", th.StringType),
    th.Property(
        "blocks",
        th.ArrayType(
            th.ObjectType(
                th.Property("type", th.StringType),
            )
        ),
    ),
    th.Property("reply_count", th.IntegerType),
    th.Property("reply_users_count", th.NumberType),
    th.Property("latest_reply", th.StringType),
    th.Property("reply_users", th.ArrayType(th.StringType)),
    th.Property("subscribed", th.BooleanType),
).to_dict()
