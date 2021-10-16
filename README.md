# tap-slack

`tap-slack` is a Singer tap for Slack.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

- [ ] `Developer TODO:` Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

```bash
pipx install tap-slack
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
The token used to authenticate against the API will require access to several API endpoints and require the following scopes:


Below is an example App Manifest that you can use for your workspace.

```
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: tap-slack
  description: Slack App to support the implementation of Singer.io tap-slack.
  long_description: This application is used for extracting channel, user, and message data from the Slack workspace via the tap-slack application. On GitHub at https://github.com/MeltanoLabs/tap-slack.
features:
  bot_user:
    display_name: Tap Slack
    always_online: false
oauth_config:
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
different rate limitations. For more information, see Slack's [rate limits documentation](https://api.slack.com/docs/rate-limits).

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

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-slack
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-slack --version
# OR run a test `elt` pipeline:
meltano elt tap-slack target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
