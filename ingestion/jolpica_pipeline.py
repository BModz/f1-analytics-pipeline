"""
Jolpica (Ergast mirror) → GCS ingestion pipeline.

Pulls F1 reference and standings data from the Jolpica API
(a community-maintained mirror of the now-defunct Ergast API).

Endpoints used:
  /f1/{season}/drivers.json              — driver biographical info
  /f1/{season}/constructors.json         — constructor (team) info
  /f1/{season}/{round}/driverStandings   — driver championship standings per round
  /f1/{season}/{round}/constructorStandings — constructor standings per round

Usage:
    python ingestion/jolpica_pipeline.py --season 2024
"""

import argparse
import time

import dlt
import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def fetch(endpoint: str, retries: int = 3) -> dict:
    """Fetch a Jolpica endpoint with basic retry logic."""
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise e


def get_round_count(season: int) -> int:
    """Return the number of completed rounds in a season."""
    data = fetch(f"{season}/races.json")
    return int(data["MRData"]["total"])


@dlt.resource(name="drivers", write_disposition="replace")
def drivers_resource(season: int):
    """One row per driver who competed in the season."""
    data = fetch(f"{season}/drivers.json?limit=100")
    drivers = data["MRData"]["DriverTable"]["Drivers"]

    print(f"  Found {len(drivers)} drivers in {season} season")

    for d in drivers:
        yield {
            "season": season,
            "driver_id": d.get("driverId"),
            "driver_code": d.get("code"),
            "permanent_number": d.get("permanentNumber"),
            "given_name": d.get("givenName"),
            "family_name": d.get("familyName"),
            "full_name": f"{d.get('givenName')} {d.get('familyName')}",
            "date_of_birth": d.get("dateOfBirth"),
            "nationality": d.get("nationality"),
            "wikipedia_url": d.get("url"),
        }


@dlt.resource(name="constructors", write_disposition="replace")
def constructors_resource(season: int):
    """One row per constructor (team) that competed in the season."""
    data = fetch(f"{season}/constructors.json")
    constructors = data["MRData"]["ConstructorTable"]["Constructors"]

    print(f"  Found {len(constructors)} constructors in {season} season")

    for c in constructors:
        yield {
            "season": season,
            "constructor_id": c.get("constructorId"),
            "name": c.get("name"),
            "nationality": c.get("nationality"),
            "wikipedia_url": c.get("url"),
        }


@dlt.resource(name="driver_standings", write_disposition="replace")
def driver_standings_resource(season: int):
    """
    Championship standings after each round — one row per driver per round.
    Enables showing how the championship evolved across the season.
    """
    total_rounds = get_round_count(season)
    print(f"  Loading driver standings for {total_rounds} rounds...")

    for round_number in range(1, total_rounds + 1):
        data = fetch(f"{season}/{round_number}/driverStandings.json")
        standings_lists = data["MRData"]["StandingsTable"].get("StandingsLists", [])

        if not standings_lists:
            continue

        standings = standings_lists[0]["DriverStandings"]

        for s in standings:
            d = s["Driver"]
            yield {
                "season": season,
                "round_number": round_number,
                "driver_id": d.get("driverId"),
                "driver_code": d.get("code"),
                "position": int(s.get("position", 0)),
                "points": float(s.get("points", 0)),
                "wins": int(s.get("wins", 0)),
            }

        time.sleep(0.2)


@dlt.resource(name="constructor_standings", write_disposition="replace")
def constructor_standings_resource(season: int):
    """
    Constructor championship standings after each round.
    One row per constructor per round.
    """
    total_rounds = get_round_count(season)
    print(f"  Loading constructor standings for {total_rounds} rounds...")

    for round_number in range(1, total_rounds + 1):
        data = fetch(f"{season}/{round_number}/constructorStandings.json")
        standings_lists = data["MRData"]["StandingsTable"].get("StandingsLists", [])

        if not standings_lists:
            continue

        standings = standings_lists[0]["ConstructorStandings"]

        for s in standings:
            c = s["Constructor"]
            yield {
                "season": season,
                "round_number": round_number,
                "constructor_id": c.get("constructorId"),
                "constructor_name": c.get("name"),
                "position": int(s.get("position", 0)),
                "points": float(s.get("points", 0)),
                "wins": int(s.get("wins", 0)),
            }

        time.sleep(0.2)


def run_pipeline(season: int):
    pipeline = dlt.pipeline(
        pipeline_name="jolpica",
        destination="filesystem",
        dataset_name=f"jolpica_{season}",
    )

    print(f"\nRunning Jolpica pipeline for {season} season...")
    print("Destination: GCS bucket f1-analytics-pipeline-raw\n")

    load_info = pipeline.run(
        [
            drivers_resource(season=season),
            constructors_resource(season=season),
            driver_standings_resource(season=season),
            constructor_standings_resource(season=season),
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
