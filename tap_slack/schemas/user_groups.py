from singer_sdk import typing as th

schema = th.PropertiesList(
    th.Property("created", th.StringType),
    th.Property("creator", th.StringType),
    th.Property("id", th.StringType),
    th.Property("is_archived", th.BooleanType),
    th.Property("is_deleted", th.BooleanType),
    th.Property("is_group", th.BooleanType),
    th.Property("is_moved", th.IntegerType),
    th.Property("is_mpim", th.BooleanType),
    th.Property("is_open", th.BooleanType),
    th.Property("is_pending_ext_shared", th.BooleanType),
    th.Property("is_read_only", th.BooleanType),
    th.Property("is_thread_only", th.BooleanType),
    th.Property("last_read", th.StringType),
    th.Property("members", th.ArrayType(th.StringType)),
    th.Property("name", th.StringType),
    th.Property("name_normalized", th.StringType),
    th.Property("num_members", th.IntegerType),
    th.Property("parent_group", th.StringType),
    th.Property("priority", th.NumberType),
    th.Property(
        "purpose",
        th.ObjectType(
            th.Property("creator", th.StringType),
            th.Property("last_set", th.IntegerType),
            th.Property("value", th.StringType),
        ),
    ),
    th.Property(
        "topic",
        th.ObjectType(
            th.Property("creator", th.StringType),
            th.Property("last_set", th.IntegerType),
            th.Property("value", th.StringType),
        ),
    ),
    th.Property("unread_count", th.IntegerType),
    th.Property("unread_count_display", th.IntegerType),
).to_dict()
