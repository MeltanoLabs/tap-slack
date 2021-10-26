# tap-slack [Under Development]

`tap-slack` is a Singer tap for Slack, built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

You can install this repository directly from the Github repo. For example, by running:

```bash
pipx install https://github.com/MeltanoLabs/tap-slack.git
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-slack --about
```

### Creating the Tap-Slack App

In order to access the records in your workspace, you will need to create a new Slack App.
Below is an example App Manifest that you can use for your workspace. If you would like to
access additional channels, such as direct messages, you will need to provide additional scopes
to your Slack app.

```
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: MeltanoLabs Tap-Slack
  description: Slack App to support the implementation of Singer.io tap-slack
  long_description: This application is used for extracting channel, user, and message data from the Slack workspace via the tap-slack application. Found on GitHub at https://github.com/MeltanoLabs/tap-slack.
features:
  bot_user:
    display_name: MeltanoLabs Tap-Slack
    always_online: false
oauth_config:
  redirect_urls:
    - https://meltano.com/
  scopes:
    bot:
      - channels:join
      - channels:history
      - channels:read
      - users:read
      - users:read.email
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

### Rate Limits

The Slack API implements a tiered rate limiting system, where certain methods operate under
different rate limitations. In this tap, rate limiting is handled by adding a pause
between API calls. For more information, see Slack's [rate limits documentation](https://api.slack.com/docs/rate-limits).

## Usage

You can easily run `tap-slack` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-slack --version
tap-slack --help
tap-slack --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_slack/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-slack` CLI interface directly using `poetry run`:

```bash
poetry run tap-slack --help
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
