"""REST client handling, including SlackStream base class."""

import datetime
import requests
import time
from typing import Any, Dict, Text, Optional

from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator


class SlackStream(RESTStream):
    """Slack stream class."""

    _page_size = 500
    url_base = "https://slack.com/api"
    max_requests_per_minute = 200
    records_jsonpath = "$[*]"
    next_page_token_jsonpath = "$.response_metadata.next_cursor"

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("api_key"),
        )

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = {}
        if next_page_token:
            params["cursor"] = next_page_token
        if self._page_size:
            params["limit"] = self._page_size
        if context and "channel_id" in context:
            params["channel"] = context["channel_id"]
        return params

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """Apply rate throttling for taps that are likely to run into issues."""
        if self.max_requests_per_minute:
            time.sleep(60.0 / self.max_requests_per_minute)
        return row
