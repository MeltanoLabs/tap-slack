import datetime
import json
import os
import pytest

from tap_slack.tap import TapSlack


@pytest.fixture
def sample_config():
    yield {
        "api_key": os.environ.get("TAP_SLACK_API_KEY"),
        "start_date": datetime.datetime.today().strftime("%Y-%m-%d"),
    }


@pytest.fixture
def tap_slack(sample_config):
    yield TapSlack(config=sample_config)


@pytest.fixture
def full_sync_records(tap_slack, capsys):
    tap_slack.sync_all()
    stdout = capsys.readouterr().out
    records = [
        json.loads(ii) for ii in stdout.split("\n")
        if "{" in ii and "}" in ii
    ]
    parsed = analyze_records(records)

    yield parsed


def analyze_records(records):
    parsed = {"raw": []}
    for record in records:
        if record["type"] != "STATE":
            if not parsed.get(record["type"]):
                parsed[record["type"]] = {}
            if not parsed[record["type"]].get(record["stream"]):
                parsed[record["type"]][record["stream"]] = {"count": 0, "raw": []}
            parsed[record["type"]][record["stream"]]["raw"].append(record)
            parsed[record["type"]][record["stream"]]["count"] += 1
        parsed["raw"].append(record)
    return parsed
