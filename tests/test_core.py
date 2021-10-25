"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_standard_tap_tests
from tap_slack.tap import TapSlack
from typing import Text, List, Dict


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests(sample_config):
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapSlack, config=sample_config)
    for test in tests:
        test()
