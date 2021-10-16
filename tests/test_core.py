"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os
import json
import pytest

from singer_sdk.testing import get_standard_tap_tests
from typing import Text, List, Dict
from tap_slack.tap import TapSlack

SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "thread_lookback_days": 7,
    "auto_join_channels": True,
}


@pytest.fixture
def tap_slack():
    return TapSlack(config=SAMPLE_CONFIG)


def parse_singer_records_from_stdout(stdout: Text) -> Dict:
    parsed = {"raw": []}
    for ii in stdout.split("\n"):
        try:
            record = json.loads(ii)
            if record["type"] != "STATE":
                if not parsed.get(record["type"]):
                    parsed[record["type"]] = {}
                if not parsed[record["type"]].get(record["stream"]):
                    parsed[record["type"]][record["stream"]] = {"count": 0, "raw": []}

                parsed[record["type"]][record["stream"]]["raw"].append(record)
                parsed[record["type"]][record["stream"]]["count"] += 1
            parsed["raw"].append(record)
        except json.decoder.JSONDecodeError as e:
            pass
    return parsed


def standard_stream_test(tap, stream_name, capsys):
    stream = tap.streams[stream_name]
    stream_catalog_keys = stream.schema["properties"].keys()
    if stream.parent_stream_type:
        tap.streams[stream.parent_stream_type.name].sync()
    else:
        stream.sync()
    parsed = parse_singer_records_from_stdout(capsys.readouterr().out)
    print(parsed)

    first_record = parsed["RECORD"][stream_name]["raw"][0]["record"]
    record_count = parsed["RECORD"][stream_name]["count"]

    assert record_count > 0

    fields_in_record_and_not_in_catalog = set(first_record.keys()) - set(
        stream_catalog_keys
    )
    fields_in_catalog_and_not_in_record = set(stream_catalog_keys) - set(
        first_record.keys()
    )

    assert fields_in_catalog_and_not_in_record == set()
    assert fields_in_record_and_not_in_catalog == set()


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapSlack, config=SAMPLE_CONFIG)
    for test in tests:
        test()


def test_channels_sync(capsys, tap_slack):
    standard_stream_test(tap_slack, "channels", capsys)


def test_channel_members_sync(capsys, tap_slack):
    standard_stream_test(tap_slack, "channel_members", capsys)


def test_messages_sync(capsys, tap_slack):
    standard_stream_test(tap_slack, "messages", capsys)


def test_threads_sync(capsys, tap_slack):
    standard_stream_test(tap_slack, "threads", capsys)


def test_users_sync(capsys, tap_slack):
    standard_stream_test(tap_slack, "users", capsys)
