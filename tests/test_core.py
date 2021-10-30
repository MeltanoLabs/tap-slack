"""Tests standard tap features using the built-in SDK tests library."""

import pytest
import os
import pytest

from tap_slack.tap import TapSlack
from tap_slack.testing import TapTestUtility


SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": "2021-09-25T00:00:00Z",
}

TEST_MANIFEST = [
    ("tap__cli", {}),
    ("tap__discovery", {}),
    ("tap__stream_connections", {}),
    ("stream__catalog_schema_matches_record", {"stream_name": "channels"}),
    ("stream__record_schema_matches_catalog", {"stream_name": "channels"}),
    ("stream__returns_record", {"stream_name": "channels"}),
    ("stream__primary_key", {"stream_name": "channels"}),
    ("stream__catalog_schema_matches_record", {"stream_name": "channel_members"}),
    ("stream__record_schema_matches_catalog", {"stream_name": "channel_members"}),
    ("stream__returns_record", {"stream_name": "channel_members"}),
    ("stream__primary_key", {"stream_name": "channel_members"}),
    ("stream__record_schema_matches_catalog", {"stream_name": "messages"}),
    ("stream__returns_record", {"stream_name": "messages"}),
    ("stream__primary_key", {"stream_name": "messages"}),
    ("stream__record_schema_matches_catalog", {"stream_name": "threads"}),
    ("stream__returns_record", {"stream_name": "threads"}),
    ("stream__primary_key", {"stream_name": "threads"}),
    ("stream__catalog_schema_matches_record", {"stream_name": "users"}),
    ("stream__record_schema_matches_catalog", {"stream_name": "users"}),
    ("stream__returns_record", {"stream_name": "users"}),
    ("stream__primary_key", {"stream_name": "users"}),
    ("attribute__unique", {"stream_name": "channels", "attribute_name": "id"}),
    ("attribute__not_null", {"stream_name": "channels", "attribute_name": "id"}),
]


def generate_id_from_test_config(c):
    test, params = c
    id_components = [params.get("stream_name"), params.get("attribute_name"), test]
    return "__".join(c for c in id_components if c)


@pytest.fixture(scope="session")
def test_util():
    test_util = TapTestUtility(TapSlack, SAMPLE_CONFIG, stream_record_limit=500)
    test_util.run_sync()

    yield test_util


@pytest.mark.parametrize(
    "test_config", TEST_MANIFEST, ids=map(generate_id_from_test_config, TEST_MANIFEST)
)
def test_builtin_tap_tests(test_util, test_config):
    test_name, params = test_config
    test_func = test_util.available_tests[test_name]
    test_func(**params)
