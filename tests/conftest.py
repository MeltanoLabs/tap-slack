import datetime
import json
import os
import pytest

from tap_slack.tap import TapSlack
from tap_slack.testing import StreamTestUtility


@pytest.fixture(scope="session")
def sample_config():
    yield {
        "api_key": os.environ.get("TAP_SLACK_API_KEY"),
        "start_date": "2021-09-25T00:00:00Z",
    }


@pytest.fixture(scope="session")
def tap_slack(sample_config):
    yield TapSlack(config=sample_config)


@pytest.fixture(scope="session")
def stream_test_util(sample_config):
    test_util = StreamTestUtility(TapSlack, sample_config)
    test_util.run_sync()

    yield test_util
