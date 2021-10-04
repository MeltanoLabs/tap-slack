from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("channel_id", th.StringType),
    th.Property("user_id", th.StringType),
).to_dict()
