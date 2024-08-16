"""REST client handling, including SlackStream base class."""

from __future__ import annotations

import time
import backoff
from typing import Any, Dict, List, Optional, Text, Generator
from http import HTTPStatus

from requests import Response
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import JSONPathPaginator
from singer_sdk.streams import RESTStream
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError


class ThrottledJSONPathPaginator(JSONPathPaginator):
    """A throttled paginator."""

    max_requests_per_minute = 200

    def get_next(self, response: Response) -> str | None:
        """Get the next page token.

        Args:
            response: API response object.

        Returns:
            The next page token.
        """
        if self.max_requests_per_minute:
            time.sleep(60.0 / self.max_requests_per_minute)
        return super().get_next(response)


class SlackStream(RESTStream):
    """Slack stream class."""

    _page_size = 500
    url_base = "https://slack.com/api"
    records_jsonpath = "$[*]"
    next_page_token_jsonpath = "$.response_metadata.next_cursor"

    @property
    def timeout(self) -> int:
        # Instead of the default 300 seconds
        return 30

    def validate_response(self, response: Response) -> None:
        """
        Override RESTStream's default validator to handle edge cases specific to Slack's API
        """
        if (
            response.status_code in self.extra_retry_statuses
            or response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR
        ):
            msg = self.response_error_message(response)
            raise RetriableAPIError(msg, response)

        if (
            HTTPStatus.BAD_REQUEST
            <= response.status_code
            < HTTPStatus.INTERNAL_SERVER_ERROR
        ):
            msg = self.response_error_message(response)
            raise FatalAPIError(msg)
        
        # Slack's API has a funny behavior in case of a bad auth token: 200 response with "invalid_auth"
        # Other errors may be acceptable, like "not_in_channel"
        try:
            parsed_res = response.json()
            if parsed_res.get("ok", True) == False and parsed_res.get("error", "") == "invalid_auth":
                raise FatalAPIError(f"Slack API error: {parsed_res.get('error','')}")
            
            if parsed_res.get("ok", True) == False and parsed_res.get("error", "") == "missing_scope":
                raise FatalAPIError(f"Slack API error: insufficient scope. {parsed_res}")
        except ValueError:
            # Do nothing, as the response might simply not be a json
            pass

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
        if self.config.get("team_id"):
            params["team_id"] = self.config.get("team_id")
        return params

    def get_new_paginator(self):
        """Override default to apply rate throttling for streams."""
        return ThrottledJSONPathPaginator(self.next_page_token_jsonpath)

    def backoff_wait_generator(self) -> Generator[float, None, None]:
        """Override the default wait generator because it tends to not wait long enough

        See for options:
        https://github.com/litl/backoff/blob/master/backoff/_wait_gen.py

        And see for examples: `Code Samples <../code_samples.html#custom-backoff>`_

        Returns:
            The wait generator
        """
        return backoff.expo(base=2, factor=2, max_value=15)