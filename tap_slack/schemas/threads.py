from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("channel_id", th.StringType, required=True),
    th.Property("thread_ts", th.StringType, required=True),
    th.Property("client_msg_id", th.StringType),
    th.Property("type", th.StringType),
    th.Property("text", th.StringType),
    th.Property("user", th.StringType),
    th.Property("ts", th.StringType),
    th.Property("team", th.StringType),
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
