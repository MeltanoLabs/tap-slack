"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_standard_tap_tests
from tap_slack.tap import TapSlack
from typing import Text, List, Dict


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests(sample_config):
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapSlack, config=sample_config)
    for test in tests:
        test()

def test_channels_stream(stream_test_util):
    stream_name = "channels"
    stream_test_util._test_stream_catalog_schema_matches_records(stream_name)
    stream_test_util._test_stream_record_schema_matches_catalog(stream_name)
    stream_test_util._test_stream_returns_at_least_one_record(stream_name)
    stream_test_util._test_stream_primary_key(stream_name)


def test_channel_members_stream(stream_test_util):
    stream_name = "channel_members"
    stream_test_util._test_stream_catalog_schema_matches_records(stream_name)
    stream_test_util._test_stream_record_schema_matches_catalog(stream_name)
    stream_test_util._test_stream_returns_at_least_one_record(stream_name)
    stream_test_util._test_stream_primary_key(stream_name)


def test_messages_stream(stream_test_util):
    stream_name = "messages"
    # stream_test_util._test_stream_catalog_schema_matches_records(stream_name)
    stream_test_util._test_stream_record_schema_matches_catalog(stream_name)
    stream_test_util._test_stream_returns_at_least_one_record(stream_name)
    stream_test_util._test_stream_primary_key(stream_name)


def test_threads_stream(stream_test_util):
    stream_name = "threads"
    # stream_test_util._test_stream_catalog_schema_matches_records(stream_name)
    stream_test_util._test_stream_record_schema_matches_catalog(stream_name)
    stream_test_util._test_stream_returns_at_least_one_record(stream_name)
    stream_test_util._test_stream_primary_key(stream_name)


def test_users_stream(stream_test_util):
    stream_name = "users"
    stream_test_util._test_stream_catalog_schema_matches_records(stream_name)
    stream_test_util._test_stream_record_schema_matches_catalog(stream_name)
    stream_test_util._test_stream_returns_at_least_one_record(stream_name)
    stream_test_util._test_stream_primary_key(stream_name)
