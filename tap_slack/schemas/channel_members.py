from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("channel_id", th.StringType, required=True),
    th.Property("user_id", th.StringType, required=True),
).to_dict()
