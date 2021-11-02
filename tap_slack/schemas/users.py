from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("id", th.StringType, required=True),
    th.Property("team_id", th.StringType),
    th.Property("name", th.StringType),
    th.Property("deleted", th.BooleanType),
    th.Property("color", th.StringType),
    th.Property("real_name", th.StringType),
    th.Property("tz", th.StringType),
    th.Property("tz_label", th.StringType),
    th.Property("tz_offset", th.IntegerType),
    th.Property("is_admin", th.BooleanType),
    th.Property("is_owner", th.BooleanType),
    th.Property("is_primary_owner", th.BooleanType),
    th.Property("is_restricted", th.BooleanType),
    th.Property("is_ultra_restricted", th.BooleanType),
    th.Property("is_bot", th.BooleanType),
    th.Property("updated", th.DateTimeType),
    th.Property("is_app_user", th.BooleanType),
    th.Property("is_email_confirmed", th.BooleanType),
    th.Property("who_can_share_contact_card", th.StringType),
    th.Property(
        "profile",
        th.ObjectType(
            th.Property("email", th.StringType),
        ),
    ),
).to_dict()
