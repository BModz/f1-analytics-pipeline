"""
Unit tests for jolpica_pipeline.py.

Tests cover retry logic and data transformation — no real HTTP calls are made.
"""

import sys
import time
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, "ingestion")

import jolpica_pipeline


def make_response(status_code: int, json_data: dict = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    else:
        resp.raise_for_status.return_value = None
    return resp


class TestFetch:
    def test_successful_request(self):
        payload = {"MRData": {"total": "24"}}
        mock_resp = make_response(200, payload)

        with patch("jolpica_pipeline.requests.get", return_value=mock_resp):
            result = jolpica_pipeline.fetch("2024/races.json")

        assert result == payload

    def test_retries_on_429_then_succeeds(self):
        resp_429 = make_response(429)
        resp_200 = make_response(200, {"data": "ok"})

        with patch("jolpica_pipeline.requests.get", side_effect=[resp_429, resp_200]):
            with patch("jolpica_pipeline.time.sleep") as mock_sleep:
                result = jolpica_pipeline.fetch("endpoint", retries=3)

        assert result == {"data": "ok"}
        mock_sleep.assert_called()

    def test_raises_after_exhausting_retries(self):
        resp_429 = make_response(429)

        with patch("jolpica_pipeline.requests.get", return_value=resp_429):
            with patch("jolpica_pipeline.time.sleep"):
                with pytest.raises(RuntimeError, match="Failed to fetch"):
                    jolpica_pipeline.fetch("endpoint", retries=2)

    def test_429_backoff_increases_with_attempt(self):
        resp_429 = make_response(429)
        resp_200 = make_response(200, {"data": "ok"})

        sleep_calls = []

        def capture_sleep(seconds):
            sleep_calls.append(seconds)

        with patch("jolpica_pipeline.requests.get", side_effect=[resp_429, resp_429, resp_200]):
            with patch("jolpica_pipeline.time.sleep", side_effect=capture_sleep):
                jolpica_pipeline.fetch("endpoint", retries=5)

        # Each 429 back-off should be larger than the previous
        assert sleep_calls[0] < sleep_calls[1]


class TestDriversTransformation:
    def test_drivers_resource_yields_correct_fields(self):
        payload = {
            "MRData": {
                "DriverTable": {
                    "Drivers": [
                        {
                            "driverId": "verstappen",
                            "code": "VER",
                            "permanentNumber": "1",
                            "givenName": "Max",
                            "familyName": "Verstappen",
                            "dateOfBirth": "1997-09-30",
                            "nationality": "Dutch",
                            "url": "http://en.wikipedia.org/wiki/Max_Verstappen",
                        }
                    ]
                }
            }
        }

        with patch("jolpica_pipeline.fetch", return_value=payload):
            rows = list(jolpica_pipeline.drivers_resource(season=2024))

        assert len(rows) == 1
        row = rows[0]
        assert row["driver_id"] == "verstappen"
        assert row["driver_code"] == "VER"
        assert row["full_name"] == "Max Verstappen"
        assert row["season"] == 2024
        assert row["nationality"] == "Dutch"

    def test_constructors_resource_yields_correct_fields(self):
        payload = {
            "MRData": {
                "ConstructorTable": {
                    "Constructors": [
                        {
                            "constructorId": "red_bull",
                            "name": "Red Bull",
                            "nationality": "Austrian",
                            "url": "http://en.wikipedia.org/wiki/Red_Bull_Racing",
                        }
                    ]
                }
            }
        }

        with patch("jolpica_pipeline.fetch", return_value=payload):
            rows = list(jolpica_pipeline.constructors_resource(season=2024))

        assert len(rows) == 1
        row = rows[0]
        assert row["constructor_id"] == "red_bull"
        assert row["name"] == "Red Bull"
        assert row["season"] == 2024
