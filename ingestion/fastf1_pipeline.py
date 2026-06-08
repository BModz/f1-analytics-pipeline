"""
FastF1 → GCS ingestion pipeline.

Loads race results and lap data for a given F1 season from the FastF1 library
and writes raw Parquet files to Google Cloud Storage via dlt.

Usage:
    python ingestion/fastf1_pipeline.py --season 2024
"""

import argparse

import dlt
import fastf1
import pandas as pd

# FastF1 local cache — avoids re-downloading data on repeated runs.
fastf1.Cache.enable_cache("exploration/cache")


def get_season_schedule(season: int) -> list[dict]:
    """Return list of completed race events for the given season."""
    schedule = fastf1.get_event_schedule(season, include_testing=False)
    # Only include rounds that have already happened (EventFormat != "unknown")
    completed = schedule[schedule["EventFormat"] != "unknown"]
    return completed.to_dict(orient="records")


@dlt.resource(name="race_results", write_disposition="replace")
def race_results_resource(season: int):
    """
    Yields one row per driver per race for the full season.
    write_disposition="replace" means each run overwrites the destination —
    safe for a small table that we always reload in full.
    """
    events = get_season_schedule(season)

    for event in events:
        round_number = event["RoundNumber"]
        event_name = event["EventName"]

        print(f"  Loading results: Round {round_number} — {event_name}")

        try:
            session = fastf1.get_session(season, round_number, "R")
            session.load(
                laps=False,
                telemetry=False,
                weather=False,
                messages=False,
            )

            results = session.results.copy()

            # Add context columns so each row is self-describing
            results["season"] = season
            results["round_number"] = round_number
            results["event_name"] = event_name
            results["event_date"] = str(event["EventDate"])
            results["circuit"] = event["Location"]
            results["country"] = event["Country"]

            # Convert ALL timedelta columns to seconds (floats) — dlt is not Timedelta-aware
            for col in results.columns:
                if pd.api.types.is_timedelta64_dtype(results[col]):
                    results[col] = results[col].apply(
                        lambda x: x.total_seconds() if pd.notna(x) else None
                    )

            # dlt expects an iterable of dicts
            for row in results.to_dict(orient="records"):
                yield row

        except Exception as e:
            print(f"  WARNING: Could not load results for round {round_number}: {e}")
            continue


@dlt.resource(name="race_laps", write_disposition="replace")
def race_laps_resource(season: int):
    """
    Yields one row per lap per driver per race for the full season.
    ~1,100 rows per race × 24 races = ~26,000 rows for a full season.
    """
    events = get_season_schedule(season)

    for event in events:
        round_number = event["RoundNumber"]
        event_name = event["EventName"]

        print(f"  Loading laps:    Round {round_number} — {event_name}")

        try:
            session = fastf1.get_session(season, round_number, "R")
            session.load(
                laps=True,
                telemetry=False,
                weather=False,
                messages=False,
            )

            laps = session.laps.copy()

            # Add context columns
            laps["season"] = season
            laps["round_number"] = round_number
            laps["event_name"] = event_name
            laps["circuit"] = event["Location"]

            # Convert ALL timedelta columns to seconds (floats) — dlt is not Timedelta-aware
            for col in laps.columns:
                if pd.api.types.is_timedelta64_dtype(laps[col]):
                    laps[col] = laps[col].apply(
                        lambda x: x.total_seconds() if pd.notna(x) else None
                    )

            # LapStartDate is a datetime — convert to string
            if "LapStartDate" in laps.columns:
                laps["LapStartDate"] = laps["LapStartDate"].astype(str)

            for row in laps.to_dict(orient="records"):
                yield row

        except Exception as e:
            print(f"  WARNING: Could not load laps for round {round_number}: {e}")
            continue


def run_pipeline(season: int):
    pipeline = dlt.pipeline(
        pipeline_name="fastf1",
        destination="filesystem",
        dataset_name=f"fastf1_{season}",
    )

    print(f"\nRunning FastF1 pipeline for {season} season...")
    print("Destination: GCS bucket f1-analytics-pipeline-raw\n")

    load_info = pipeline.run(
        [
            race_results_resource(season=season),
            race_laps_resource(season=season),
        ],
        loader_file_format="parquet",
    )

    print("\n--- Load complete ---")
    print(load_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2024)
    args = parser.parse_args()

    run_pipeline(season=args.season)
