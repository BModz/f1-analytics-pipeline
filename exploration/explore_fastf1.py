"""
FastF1 data exploration script.
Run this manually to understand what data is available before building the pipeline.
Not part of the production pipeline.
"""

import fastf1
import pandas as pd

# FastF1 caches raw data locally so repeat runs don't re-download.
# The cache folder is gitignored.
fastf1.Cache.enable_cache("exploration/cache")

print("=" * 60)
print("Loading 2024 Bahrain GP Race session...")
print("(First run downloads data — may take 30-60 seconds)")
print("=" * 60)

session = fastf1.get_session(2024, "Bahrain", "R")
session.load()

# --- 1. Session info ---
print("\n--- SESSION INFO ---")
print(f"Event:    {session.event['EventName']}")
print(f"Date:     {session.event['EventDate']}")
print(f"Circuit:  {session.event['Location']}")
print(f"Season:   {session.event.year}")

# --- 2. Results (driver finishing positions) ---
print("\n--- RACE RESULTS (first 5 rows) ---")
results = session.results
print(results[["DriverNumber", "Abbreviation", "FullName", "TeamName", "Position", "Points", "Status"]].head())
print(f"\nTotal drivers: {len(results)}")
print(f"Columns available: {list(results.columns)}")

# --- 3. Laps data ---
print("\n--- LAPS DATA (first 5 rows) ---")
laps = session.laps
print(laps[["Driver", "LapNumber", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "Compound", "TyreLife"]].head())
print(f"\nTotal lap rows: {len(laps)}")
print(f"Columns available: {list(laps.columns)}")

# --- 4. Fastest lap overall ---
print("\n--- FASTEST LAP ---")
fastest = laps.pick_fastest()
print(f"Driver:    {fastest['Driver']}")
print(f"Lap time:  {fastest['LapTime']}")
print(f"Lap #:     {fastest['LapNumber']}")

# --- 5. Single driver laps ---
print("\n--- VER LAP TIMES (first 5) ---")
ver_laps = laps.pick_drivers("VER")
print(ver_laps[["LapNumber", "LapTime", "Compound", "TyreLife", "SpeedFL"]].head())

# --- 6. Telemetry sample (one lap) ---
print("\n--- TELEMETRY SAMPLE (fastest lap, first 5 rows) ---")
telemetry = fastest.get_telemetry()
print(telemetry[["Time", "Speed", "Throttle", "Brake", "nGear", "DRS"]].head())
print(f"\nTotal telemetry rows for this lap: {len(telemetry)}")
print(f"Telemetry columns: {list(telemetry.columns)}")

print("\n" + "=" * 60)
print("Exploration complete.")
print("=" * 60)
