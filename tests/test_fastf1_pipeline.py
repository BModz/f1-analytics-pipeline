"""
Unit tests for fastf1_pipeline.py.

Tests focus on the timedelta conversion logic — the most bug-prone
transformation in the pipeline (dlt cannot serialise pandas Timedelta).
"""

import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.insert(0, "ingestion")

import fastf1_pipeline


class TestTimedeltaConversion:
    """The pipeline converts all timedelta columns to float seconds."""

    def _make_session_mock(self, df: pd.DataFrame, weather_df: pd.DataFrame = None):
        session = MagicMock()
        session.results = df
        session.weather_data = weather_df if weather_df is not None else pd.DataFrame()
        return session

    def test_timedelta_columns_converted_to_seconds(self):
        df = pd.DataFrame(
            {
                "season": [2024],
                "round_number": [1],
                "event_name": ["Bahrain Grand Prix"],
                "event_date": ["2024-03-02"],
                "circuit": ["Sakhir"],
                "country": ["Bahrain"],
                "DriverNumber": ["1"],
                "Abbreviation": ["VER"],
                "FullName": ["Max Verstappen"],
                "TeamName": ["Red Bull Racing"],
                "Position": [1],
                "GridPosition": [1],
                "Points": [25.0],
                "Status": ["Finished"],
                "Time": [pd.Timedelta(seconds=5765.1)],
            }
        )

        schedule_entry = {
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
            "EventDate": "2024-03-02",
            "Location": "Sakhir",
            "Country": "Bahrain",
        }

        with patch("fastf1_pipeline.get_season_schedule", return_value=[schedule_entry]):
            with patch("fastf1_pipeline.fastf1.get_session") as mock_get_session:
                mock_session = self._make_session_mock(df)
                mock_get_session.return_value = mock_session

                rows = list(fastf1_pipeline.race_results_resource(season=2024))

        assert len(rows) == 1
        assert isinstance(rows[0]["Time"], float)
        assert abs(rows[0]["Time"] - 5765.1) < 0.01

    def test_null_timedelta_becomes_none(self):
        df = pd.DataFrame(
            {
                "season": [2024],
                "round_number": [1],
                "event_name": ["Bahrain Grand Prix"],
                "event_date": ["2024-03-02"],
                "circuit": ["Sakhir"],
                "country": ["Bahrain"],
                "DriverNumber": ["11"],
                "Abbreviation": ["PER"],
                "FullName": ["Sergio Perez"],
                "TeamName": ["Red Bull Racing"],
                "Position": [None],
                "GridPosition": [2],
                "Points": [0.0],
                "Status": ["Accident"],
                "Time": pd.array([pd.NaT], dtype="timedelta64[ns]"),
            }
        )

        schedule_entry = {
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
            "EventDate": "2024-03-02",
            "Location": "Sakhir",
            "Country": "Bahrain",
        }

        with patch("fastf1_pipeline.get_season_schedule", return_value=[schedule_entry]):
            with patch("fastf1_pipeline.fastf1.get_session") as mock_get_session:
                mock_session = self._make_session_mock(df)
                mock_get_session.return_value = mock_session

                rows = list(fastf1_pipeline.race_results_resource(season=2024))

        assert rows[0]["Time"] is None

    def test_failed_round_is_skipped(self):
        """If FastF1 raises for a round, it should be skipped rather than crashing."""
        schedule = [
            {"RoundNumber": 1, "EventName": "Round 1", "EventDate": "2024-03-02",
             "Location": "X", "Country": "Y"},
            {"RoundNumber": 2, "EventName": "Round 2", "EventDate": "2024-03-09",
             "Location": "X", "Country": "Y"},
        ]

        good_df = pd.DataFrame(
            {
                "season": [2024], "round_number": [2], "event_name": ["Round 2"],
                "event_date": ["2024-03-09"], "circuit": ["X"], "country": ["Y"],
                "DriverNumber": ["1"], "Abbreviation": ["VER"], "FullName": ["Max Verstappen"],
                "TeamName": ["Red Bull"], "Position": [1], "GridPosition": [1],
                "Points": [25.0], "Status": ["Finished"],
            }
        )

        def side_effect(season, round_number, session_type):
            session = MagicMock()
            if round_number == 1:
                session.load.side_effect = Exception("Session not available")
            else:
                session.results = good_df
            return session

        with patch("fastf1_pipeline.get_season_schedule", return_value=schedule):
            with patch("fastf1_pipeline.fastf1.get_session", side_effect=side_effect):
                rows = list(fastf1_pipeline.race_results_resource(season=2024))

        assert len(rows) == 1
        assert rows[0]["round_number"] == 2
