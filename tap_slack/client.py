"""REST client handling, including SlackStream base class."""

import requests
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
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

    # def get_next_page_token(
    #     self, response: requests.Response, previous_token: Optional[Any]
    # ) -> Optional[Any]:
    #     """Return a token for identifying next page or None if no more pages."""
    #     # TODO: If pagination is required, return a token which can be used to get the
    #     #       next page. If this is the final page, return "None" to end the
    #     #       pagination loop.
    #     if self.next_page_token_jsonpath:
    #         all_matches = extract_jsonpath(
    #             self.next_page_token_jsonpath, response.json()
    #         )
    #         first_match = next(iter(all_matches), None)
    #         next_page_token = first_match
    #     else:
    #         next_page_token = response.headers.get("X-Next-Page", None)

    #     return next_page_token

    # def prepare_request_payload(
    #     self, context: Optional[dict], next_page_token: Optional[Any]
    # ) -> Optional[dict]:
    #     """Prepare the data payload for the REST API request.

    #     By default, no payload will be sent (return None).
    #     """
    #     # TODO: Delete this method if no payload is required. (Most REST APIs.)
    #     return None

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """Apply rate throttling for taps that are likely to run into issues."""
        if self.max_requests_per_minute:
            time.sleep(60.0 / self.max_requests_per_minute)
        return row
