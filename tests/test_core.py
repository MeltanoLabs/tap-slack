"""Tests standard tap features using the built-in SDK tests library."""

import pytest
import os
import pytest

from tap_slack.tap import TapSlack
from tap_slack.testing import StreamTestUtility



SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": "2021-09-25T00:00:00Z",
}

TEST_MANIFEST = [
    ("tap", "cli", {}),
    ("tap", "discovery", {}),
    ("tap", "stream_connections", {}),
    ("stream", "catalog_schema_matches_record", {"stream_name": "channels"}),
    ("stream", "record_schema_matches_catalog", {"stream_name": "channels"}),
    ("stream", "returns_record", {"stream_name": "channels"}),
    ("stream", "primary_key", {"stream_name": "channels"}),
    ("stream", "catalog_schema_matches_record", {"stream_name": "channel_members"}),
    ("stream", "record_schema_matches_catalog", {"stream_name": "channel_members"}),
    ("stream", "returns_record", {"stream_name": "channel_members"}),
    ("stream", "primary_key", {"stream_name": "channel_members"}),
    ("stream", "catalog_schema_matches_record", {"stream_name": "messages"}),
    ("stream", "record_schema_matches_catalog", {"stream_name": "messages"}),
    ("stream", "returns_record", {"stream_name": "messages"}),
    ("stream", "primary_key", {"stream_name": "messages"}),
    ("stream", "catalog_schema_matches_record", {"stream_name": "threads"}),
    ("stream", "record_schema_matches_catalog", {"stream_name": "threads"}),
    ("stream", "returns_record", {"stream_name": "threads"}),
    ("stream", "primary_key", {"stream_name": "threads"}),
    ("stream", "catalog_schema_matches_record", {"stream_name": "users"}),
    ("stream", "record_schema_matches_catalog", {"stream_name": "users"}),
    ("stream", "returns_record", {"stream_name": "users"}),
    ("stream", "primary_key", {"stream_name": "users"}),
    ("attribute", "unique", {"stream_name": "channels", "attribute_name": "id"}),
    ("attribute", "not_null", {"stream_name": "channels", "attribute_name": "id"}),
]

@pytest.fixture(scope="session")
def tap_slack():
    yield TapSlack(config=SAMPLE_CONFIG)


@pytest.fixture(scope="session")
def test_util():
    test_util = StreamTestUtility(TapSlack, SAMPLE_CONFIG)
    test_util.run_sync()

    yield test_util


@pytest.mark.parametrize("test_config", TEST_MANIFEST)
def test_builtin_tap_tests(test_util, test_config):
    level, name, params = test_config
    test_func = test_util.available_tests[level][name]
    test_func(**params)
