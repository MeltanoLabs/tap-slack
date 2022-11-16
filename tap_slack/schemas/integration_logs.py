from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("user_id", th.StringType, required=True),
    th.Property("user_name", th.StringType),
    th.Property("date", th.StringType),
    th.Property("change_type", th.StringType),
    th.Property("app_type", th.StringType),
    th.Property("app_id", th.StringType),
).to_dict()