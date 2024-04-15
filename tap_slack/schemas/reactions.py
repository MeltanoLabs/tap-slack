from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("id", th.StringType, required=True),
    th.Property("channel_id", th.StringType, required=True),
    th.Property(
        "ts",
        th.StringType,
        required=True,
        description="Epoch timestamp of when the message was posted.",
    ),
    th.Property(
        "thread_ts",
        th.StringType,
        description="Epoch timestamp of when the thread reply was posted, if applicable.",
    ),
    th.Property("reaction", th.StringType),
    th.Property("user", th.StringType),
    th.Property("original_msg_author", th.StringType),
).to_dict()
