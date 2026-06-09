"""
Unit tests for jolpica_pipeline.py.

Tests cover retry logic and data transformation — no real HTTP calls are made.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "ingestion")

import jolpica_pipeline


class MockResponse:
    """Plain response stub — avoids MagicMock attribute quirks across Python versions."""

    def __init__(self, status_code: int, json_data: dict = None):
        self.status_code = status_code
        self._json_data = json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


class TestFetch:
    def test_successful_request(self):
        payload = {"MRData": {"total": "24"}}

        with patch("jolpica_pipeline.requests.get", return_value=MockResponse(200, payload)):
            result = jolpica_pipeline.fetch("2024/races.json")

        assert result == payload

    def test_retries_on_429_then_succeeds(self):
        responses = [MockResponse(429), MockResponse(200, {"data": "ok"})]

        with patch("jolpica_pipeline.requests.get", side_effect=responses):
            with patch("jolpica_pipeline.time.sleep") as mock_sleep:
                result = jolpica_pipeline.fetch("endpoint", retries=3)

        assert result == {"data": "ok"}
        mock_sleep.assert_called()

    def test_raises_after_exhausting_retries(self):
        with patch("jolpica_pipeline.requests.get", return_value=MockResponse(429)):
            with patch("jolpica_pipeline.time.sleep"):
                with pytest.raises(RuntimeError, match="Failed to fetch"):
                    jolpica_pipeline.fetch("endpoint", retries=2)

    def test_429_backoff_increases_with_attempt(self):
        responses = [MockResponse(429), MockResponse(429), MockResponse(200, {"data": "ok"})]
        sleep_calls = []

        with patch("jolpica_pipeline.requests.get", side_effect=responses):
            with patch("jolpica_pipeline.time.sleep", side_effect=sleep_calls.append):
                jolpica_pipeline.fetch("endpoint", retries=5)

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
