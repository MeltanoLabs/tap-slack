"""Tests standard tap features using the built-in SDK tests library."""

import pytest
import os

from tap_slack.tap import TapSlack
from tap_slack.testing import TapTestUtility


SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": "2021-09-25T00:00:00Z",
}

SAMPLE_TAP = TapTestUtility(TapSlack, SAMPLE_CONFIG)
SAMPLE_TAP.tap.run_discovery()
pytest_params = SAMPLE_TAP.generate_built_in_tests()


@pytest.fixture(scope="session")
def test_util():
    test_util = TapTestUtility(TapSlack, SAMPLE_CONFIG, stream_record_limit=500)
    test_util.run_sync()

    yield test_util


@pytest.mark.parametrize("test_config", **pytest_params)
def test_builtin_tap_tests(test_util, test_config):
    test_name, params = test_config
    test_func = test_util.available_tests[test_name]
    test_func(**params)
