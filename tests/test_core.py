"""Tests standard tap features using the built-in SDK tests library."""

import pytest
import os
from unittest.mock import patch

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


@patch("tap_slack.streams.ChannelsStream._join_channel")
def test_auto_join_channel_false(patch_obj, test_util):
    test_utility.run_sync()
    patch_obj.assert_not_called()

@patch("tap_slack.streams.ChannelsStream._join_channel")
def test_auto_join_channel(patch_obj, test_util):
    config = SAMPLE_CONFIG.copy()
    config["auto_join_channels"] = True
    test_utility = TapTestUtility(TapSlack, config, stream_record_limit=500)
    test_utility.run_sync()
    patch_obj.assert_called()
