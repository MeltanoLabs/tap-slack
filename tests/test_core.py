"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_standard_tap_tests

from tap_slack.tap import TapSlack

SAMPLE_CONFIG = {
    "api_key": os.env.get("API_KEY"),
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "thread_lookback_days": 14,
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapSlack, config=SAMPLE_CONFIG)
    for test in tests:
        test()
