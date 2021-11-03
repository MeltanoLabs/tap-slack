"""REST client handling, including SlackStream base class."""

import time
from typing import Any, Dict, Text, Optional, List

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

    @property
    def expectations(self) -> List[str]:
        return [
            "stream__returns_record",
            "stream__record_schema_matches_catalog",
            "stream__primary_key",
        ]

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
        if context and "thread_ts" in context:
            params["ts"] = context["thread_ts"]
        return params

    def get_next_page_token(self, response, previous_token):
        """Override default to apply rate throttling for streams."""
        token = super().get_next_page_token(response, previous_token)
        if self.max_requests_per_minute:
            time.sleep(60.0 / self.max_requests_per_minute)
        return token
