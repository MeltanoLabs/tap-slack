"""REST client handling, including SlackStream base class."""

import time
from typing import Any, Dict, Optional

from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator


class SlackStream(RESTStream):
    """Slack stream class."""

    url_base = "https://slack.com/api"
    _page_size = 500
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

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["cursor"] = next_page_token
        if self._page_size:
            params["limit"] = self._page_size
        return params

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """Apply rate throttling for taps that are likely to run into issues."""
        if self.max_requests_per_minute:
            time.sleep(60.0 / self.max_requests_per_minute)
        return row
