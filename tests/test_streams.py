def stream_record_comparison(tap, stream_name, full_sync_records):
    "The full sync of the stream should have returned at least 1 record."
    record_count = full_sync_records["RECORD"][stream_name]["count"]

    assert record_count > 0


def stream_schema_comparison(tap, stream_name, full_sync_records):
    "The stream's first record should have a catalog identical to that defined."
    stream = tap.streams[stream_name]
    first_record = full_sync_records["RECORD"][stream_name]["raw"][0]["record"]
    stream_catalog_keys = stream.schema["properties"].keys()
    fields_in_record_and_not_in_catalog = set(first_record.keys()) - set(
        stream_catalog_keys
    )
    fields_in_catalog_and_not_in_record = set(stream_catalog_keys) - set(
        first_record.keys()
    )

    print("Fields in catalog, not in record: ", fields_in_catalog_and_not_in_record)
    print("Fields in record, not in catalog: ", fields_in_record_and_not_in_catalog)

    assert fields_in_catalog_and_not_in_record == set()
    assert fields_in_record_and_not_in_catalog == set()


def test_channels_stream(tap_slack, full_sync_records):
    stream_record_comparison(tap_slack, "channels", full_sync_records)
    stream_schema_comparison(tap_slack, "channels", full_sync_records)

def test_channel_members_stream(tap_slack, full_sync_records):
    stream_record_comparison(tap_slack, "channel_members", full_sync_records)
    stream_schema_comparison(tap_slack, "channel_members", full_sync_records)

def test_messages_stream(tap_slack, full_sync_records):
    stream_record_comparison(tap_slack, "messages", full_sync_records)

def test_threads_stream(tap_slack, full_sync_records):
    stream_record_comparison(tap_slack, "threads", full_sync_records)
    stream_schema_comparison(tap_slack, "threads", full_sync_records)

def test_users_stream(tap_slack, full_sync_records):
    stream_record_comparison(tap_slack, "users", full_sync_records)
    stream_schema_comparison(tap_slack, "users", full_sync_records)
