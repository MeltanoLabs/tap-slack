"""Tests standard tap features using the built-in SDK tests library."""

import pytest
import os

from tap_slack.tap import TapSlack
from tap_slack.testing import TapTestUtility


SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": "2021-09-25T00:00:00Z",
}

test_utility = TapTestUtility(TapSlack, SAMPLE_CONFIG, stream_record_limit=500)
test_utility.tap.run_discovery()
test_utility.run_sync()

pytest_params = test_utility.generate_built_in_tests()


@pytest.fixture(scope="session")
def test_util():
    yield test_utility


@pytest.mark.parametrize("test_config", **pytest_params)
def test_builtin_tap_tests(test_util, test_config):
    test_name, params = test_config
    test_func = test_util.available_tests[test_name]
    test_func(**params)
