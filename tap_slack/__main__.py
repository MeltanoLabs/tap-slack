"""ServiceTitan entry point."""

from __future__ import annotations

from tap_slack.tap import TapSlack

TapSlack.cli()
