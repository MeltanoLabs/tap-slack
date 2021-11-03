"""Pre-built test functions which can be applied to multiple taps."""

import json
import sys
import io
import warnings

from copy import deepcopy
from collections import defaultdict
from dateutil import parser
from typing import List, Type, Any, Tuple

from singer_sdk.tap_base import Tap
from singer_sdk.exceptions import MaxRecordsLimitException


class TapTestUtility(object):
    """
    This utility class enables developers to more easily test taps against
    live integrations. It provides some out-of-the-box tests that can be run
    against individual streams, and developers can leverage the output data for
    custom tests.

    It is intended to be used as a testing fixture to simplify data testing. For example:

    ```
    @pytest.fixture(scope="session")
    def tap_test_util():
        test_util = StreamTestUtility(MyTap, config={})
        test_util.run_sync()

        yield test_util

    def test_standard_tests_for_my_stream(tap_test_util):
        test_util._test_stream_returns_at_least_one_record("my_stream")
        test_util._test_stream_catalog_attributes_in_records("my_stream")
        test_util._test_primary_keys("my_stream")
        test_util._test_stream_attribute_is_not_null("my_stream", "my_column")
    ```
    """

    schema_messages = []
    state_messages = []
    records = defaultdict(list)

    def __init__(
        self,
        tap_class: Type[Tap],
        config: dict = {},
        stream_record_limit: int = 10,
        parse_env_config: bool = True,
    ) -> None:
        """
        Initializes the test utility.

        Args:
            tap_class (Type[Tap]): Tap class to be tested
            config (dict, optional): Tap configuration for testing. Defaults to {}.
            stream_record_limit (int, optional): The max number of records a stream may emit before being stopped. Defaults to 10.
            parse_env_config (bool, optional): Whether to use env variables when initializing the tap. Defaults to True.
        """
        self.config = config
        self.tap_class = tap_class
        self.parse_env_config = parse_env_config
        self.tap = self.create_new_tap()
        self.stream_record_limit = stream_record_limit

    def create_new_tap(self, **kwargs):
        tap = self.tap_class(
            config=self.config, parse_env_config=self.parse_env_config, **kwargs
        )
        return tap

    def run_sync(self):
        stdout = self._exec_sync()
        records = self._clean_sync_output(stdout)
        self._parse_records(records)

    def _exec_sync(self) -> List[dict]:
        "Executes the sync and captures the records printed to stdout."
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        self._sync_all_streams()
        sys.stdout = sys.__stdout__
        return output_buffer.getvalue()

    def _sync_all_streams(self) -> bool:
        """
        Rewrites the
        """
        self.tap._reset_state_progress_markers()
        self.tap._set_compatible_replication_methods()
        for stream in self.tap.streams.values():
            stream._MAX_RECORDS_LIMIT = self.stream_record_limit
            if not stream.selected and not stream.has_selected_descendents:
                self.tap.logger.info(f"Skipping deselected stream '{stream.name}'.")
                continue

            if stream.parent_stream_type:
                self.tap.logger.debug(
                    f"Child stream '{type(stream).__name__}' is expected to be called "
                    f"by parent stream '{stream.parent_stream_type.__name__}'. "
                    "Skipping direct invocation."
                )
                continue

            try:
                stream.sync()
            except MaxRecordsLimitException:
                pass
            stream.finalize_state_progress_markers()
        self.tap.logger.info("Completed sync")
        return True

    def _clean_sync_output(self, raw_records):
        lines = raw_records.strip().split("\n")
        return [json.loads(ii) for ii in lines]

    def _parse_records(self, records: List[dict]) -> None:
        self.raw_messages = records
        for record in records:
            if record["type"] == "STATE":
                self.state_messages.append(record)
                continue
            if record["type"] == "SCHEMA":
                self.schema_messages.append(record)
                continue
            if record["type"] == "RECORD":
                stream_name = record["stream"]
                self.records[stream_name].append(record)
                continue
        return

    @property
    def available_tests(self):
        return {
            "tap__cli": self._test_tap_cli_prints,
            "tap__discovery": self._test_tap_discovery,
            "tap__stream_connections": self._test_tap_stream_connections,
            "stream__returns_record": self._test_stream_returns_at_least_one_record,
            "stream__catalog_schema_matches_record": self._test_stream_catalog_schema_matches_records,
            "stream__record_schema_matches_catalog": self._test_stream_record_schema_matches_catalog,
            "stream__primary_key": self._test_stream_primary_key,
            "attribute__not_null": self._test_stream_attribute_is_not_null,
            "attribute__unique": self._test_stream_attribute_is_unique,
            "attribute__accepted_values": self._test_stream_attribute_contains_accepted_values,
            "attribute__valid_timestamp": self._test_stream_attribute_is_valid_timestamp,
            "attribute__is_object": self._test_stream_attribute_is_object,
            "attribute__is_integer": self._test_stream_attribute_is_integer,
            "attribute__is_boolean": self._test_stream_attribute_is_boolean,
        }

    def generate_built_in_tests(self):
        tap_tests = self._generate_tap_tests()
        schema_tests = self._generate_schema_tests()
        attribute_tests = self._generate_attribute_tests()
        test_manifest = tap_tests + schema_tests + attribute_tests
        test_ids = self._generate_test_ids(test_manifest)
        return {"argvalues": test_manifest, "ids": test_ids}

    def _generate_tap_tests(self):
        manifest = []
        for test_name in self.tap.expectations:
            manifest.append((test_name, {}))
        return manifest

    def _generate_schema_tests(self):
        manifest = []
        for stream in self.tap.streams.values():
            for test_name in stream.expectations:
                manifest.append((test_name, {"stream_name": stream.name}))
        return manifest

    def _generate_attribute_tests(self):
        manifest = []
        for stream in self.tap.streams.values():
            schema = stream.schema
            for k, v in schema["properties"].items():
                params = {"stream_name": stream.name, "attribute_name": k}
                if v.get("required"):
                    manifest.append(("attribute__unique", params))
                if v.get("format") == "date-time":
                    manifest.append(("attribute__valid_timestamp", params))
                if not "null" in v.get("type", []):
                    manifest.append(("attribute__not_null", params))
                if "boolean" in v.get("type", []):
                    manifest.append(("attribute__is_boolean", params))
                if "integer" in v.get("type", []):
                    manifest.append(("attribute__is_integer", params))
                if "object" in v.get("type", []):
                    manifest.append(("attribute__is_object", params))
        return manifest

    def _generate_test_ids(self, test_manifest):
        id_list = []
        for test, params in test_manifest:
            id_components = [
                params.get("stream_name"),
                params.get("attribute_name"),
                test,
            ]
            id_list.append("__".join(c for c in id_components if c))
        return id_list

    def _test_tap_cli_prints(self) -> None:
        # Test CLI prints
        tap = self.create_new_tap()
        tap.print_version()
        tap.print_about()
        tap.print_about(format="json")

    def _test_tap_discovery(self) -> None:
        # Test discovery
        tap1 = self.create_new_tap()
        tap1.run_discovery()
        catalog = tap1.catalog_dict
        # Reset and re-initialize with an input catalog
        tap2: Tap = self.create_new_tap(catalog=catalog)
        assert tap2

    def _test_tap_stream_connections(self) -> None:
        # Initialize with basic config
        tap = self.create_new_tap()
        tap.run_connection_test()

    def _test_stream_returns_at_least_one_record(self, stream_name):
        "The full sync of the stream should have returned at least 1 record."
        record_count = len(self.records[stream_name])

        assert record_count > 0

    def _test_stream_catalog_schema_matches_records(self, stream_name):
        "The stream's first record should have a catalog identical to that defined."
        stream = self.tap.streams[stream_name]
        stream_catalog_keys = set(stream.schema["properties"].keys())
        stream_record_keys = set().union(
            *(d["record"].keys() for d in self.records[stream_name])
        )
        diff = stream_catalog_keys - stream_record_keys

        assert diff == set(), f"Fields in catalog but not in record: ({diff})"

    def _test_stream_record_schema_matches_catalog(self, stream_name):
        "The stream's first record should have a catalog identical to that defined."
        stream = self.tap.streams[stream_name]
        stream_catalog_keys = set(stream.schema["properties"].keys())
        stream_record_keys = set().union(
            *(d["record"].keys() for d in self.records[stream_name])
        )
        diff = stream_record_keys - stream_catalog_keys

        assert diff == set(), f"Fields in records but not in catalog: ({diff})"

    def _test_stream_primary_key(self, stream_name: str):
        "Test that all records for a stream's primary key are unique and non-null."
        primary_keys = self.tap.streams[stream_name].primary_keys
        records = [r["record"] for r in self.records[stream_name]]
        record_ids = []
        for r in self.records[stream_name]:
            id = (r["record"][k] for k in primary_keys)
            record_ids.append(id)

        assert len(set(record_ids)) == len(records)
        assert all(all(k is not None for k in pk) for pk in record_ids)

    def _test_stream_attribute_contains_accepted_values(
        self, stream_name: str, attribute_name: str, accepted_values: List[Any]
    ):
        "Test that a given attribute contains only accepted values."
        records = [r["record"] for r in self.records[stream_name]]

        assert all(r.get(attribute_name) in accepted_values for r in records)

    def _test_stream_attribute_is_unique(self, stream_name: str, attribute_name: str):
        "Test that a given attribute contains unique values, ignoring nulls."
        records = [r["record"] for r in self.records[stream_name]]
        values = [
            r.get(attribute_name) for r in records if r.get(attribute_name) is not None
        ]
        if not values:
            warnings.warn(UserWarning("No records were available to test."))
            return

        assert len(set(values)) == len(values)

    def _test_stream_attribute_is_valid_timestamp(
        self, stream_name: str, attribute_name: str
    ):
        "Test that a given attribute contains unique values, ignoring nulls."
        records = [r["record"] for r in self.records[stream_name]]
        values = [
            r.get(attribute_name) for r in records if r.get(attribute_name) is not None
        ]

        assert all(parser.parse(v) for v in values)

    def _test_stream_attribute_is_not_null(self, stream_name: str, attribute_name: str):
        "Test that a given attribute does not contain any null values."
        records = [r["record"] for r in self.records[stream_name]]

        assert all(r.get(attribute_name) is not None for r in records)

    def _test_stream_attribute_is_boolean(self, stream_name: str, attribute_name: str):
        "Test that a given attribute does not contain any null values."
        for record in self.records[stream_name]:
            r = record["record"]
            if r.get(attribute_name) is not None:
                assert type(bool(r[attribute_name])) == bool, \
                    f"Unable to cast value ('{r[attribute_name]}') to boolean type."

    def _test_stream_attribute_is_object(self, stream_name: str, attribute_name: str):
        "Test that a given attribute does not contain any null values."
        for record in self.records[stream_name]:
            r = record["record"]
            if r.get(attribute_name) is not None:
                assert dict(r[attribute_name]), \
                    f"Unable to cast value ('{r[attribute_name]}') to dict type."

    def _test_stream_attribute_is_integer(self, stream_name: str, attribute_name: str):
        "Test that a given attribute can be converted to an integer type."
        for record in self.records[stream_name]:
            r = record["record"]
            if r.get(attribute_name) is not None:
                assert int(r[attribute_name]), \
                    f"Unable to cast value ('{r[attribute_name]}') to int type."

    def _test_stream_attribute_is_number(self, stream_name: str, attribute_name: str):
        "Test that a given attribute can be converted to a floating point number type."
        for record in self.records[stream_name]:
            r = record["record"]
            if r.get(attribute_name) is not None:
                assert float(r.get(attribute_name)), \
                    f"Unable to cast value ('{r[attribute_name]}') to float type."