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
    th.Property(
        "edited",
        th.ObjectType(
            th.Property("user", th.StringType),
            th.Property("ts", th.StringType),
        )
    ),
    th.Property("files", th.ArrayType(th.ObjectType())),
    th.Property("upload", th.BooleanType),
    th.Property("parent_user_id", th.StringType),
    th.Property("display_as_bot", th.BooleanType),
    th.Property("is_locked", th.BooleanType),
    th.Property(
        "blocks",
        th.ArrayType(
            th.ObjectType(
                th.Property("block_id", th.StringType),
                th.Property("type", th.StringType),
                # th.Property("elements", th.ArrayType(th.AnyType)),
            )
        ),
    ),
    th.Property("subtype", th.StringType),
    th.Property("bot_id", th.StringType),
    th.Property("bot_profile", th.AnyType),
    # th.Property("root", th.StringType),
    th.Property("app_id", th.StringType),
    th.Property("reactions", th.ArrayType(th.AnyType)),
    th.Property("reply_count", th.IntegerType),
    th.Property("reply_users_count", th.NumberType),
    th.Property("latest_reply", th.StringType),
    th.Property("reply_users", th.ArrayType(th.StringType)),
    th.Property("subscribed", th.BooleanType),
).to_dict()
