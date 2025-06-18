"""Tests standard tap features using the built-in SDK tests library."""

import os
import datetime

from tap_slack.tap import TapSlack

from singer_sdk.testing import SuiteConfig, get_tap_test_class


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
