import datetime
import json
import os
import pytest

from tap_slack.tap import TapSlack
from tap_slack.testing import StreamTestUtility


SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": "2021-09-25T00:00:00Z",
}

@pytest.fixture(scope="session")
def tap_slack():
    yield TapSlack(config=SAMPLE_CONFIG)


@pytest.fixture(scope="session")
def stream_test_util():
    test_util = StreamTestUtility(TapSlack, SAMPLE_CONFIG)
    test_util.run_sync()

    yield test_util


def pytest_generate_tests(metafunc):
    stream_names = ["channels", "users", "messages", "channel_members", "threads"]
    if "stream_tests" in metafunc.fixturenames:
        if "stream_name" in metafunc.fixturenames:
            metafunc.parametrize("stream_name", stream_names)
        else:
            raise Exception("stream_name is required parameter for this test.")


@pytest.fixture
def stream_tests(stream_name):
    tests = {
        "channels": {
            "stream_tests": [
                "_test_stream_catalog_schema_matches_records",
                "_test_stream_record_schema_matches_catalog",
                "_test_stream_returns_at_least_one_record",
                "_test_stream_primary_key"
            ],
            "attribute_tests": {
                "id": [
                    "_test_stream_attribute_is_unique",
                    "_test_stream_attribute_is_not_null"
                ]
            }
        },
        "channel_members": {
            "stream_tests": [
                "_test_stream_catalog_schema_matches_records",
                "_test_stream_record_schema_matches_catalog",
                "_test_stream_returns_at_least_one_record",
                "_test_stream_primary_key"
            ],
            "attribute_tests": {}
        },
        "messages": {
            "stream_tests": [
                "_test_stream_catalog_schema_matches_records",
                "_test_stream_record_schema_matches_catalog",
                "_test_stream_returns_at_least_one_record",
                "_test_stream_primary_key"
            ],
            "attribute_tests": {}
        },
        "threads": {
            "stream_tests": [],
            "attribute_tests": {}
        },
        "users": {
            "stream_tests": [
                "_test_stream_primary_key"
            ],
            "attribute_tests": {}
        },
    }

    yield tests[stream_name]


