"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_slack.tap import TapSlack

SAMPLE_CONFIG = {
    "api_key": os.environ.get("TAP_SLACK_API_KEY"),
    "start_date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
}


TestTapSlack = get_tap_test_class(
    TapSlack,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "channels",
            "messages",
            "threads",
        ],
    ),
)
