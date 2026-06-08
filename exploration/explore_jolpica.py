"""
Jolpica/Ergast API exploration script.
Explores available endpoints before building the pipeline.
Base URL: https://api.jolpi.ca/ergast/f1/
"""

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def fetch(endpoint: str) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


print("=" * 60)
print("Jolpica/Ergast API exploration — 2024 season")
print("=" * 60)

# --- 1. Drivers ---
print("\n--- DRIVERS (first 5) ---")
data = fetch("2024/drivers.json?limit=5")
drivers = data["MRData"]["DriverTable"]["Drivers"]
for d in drivers:
    print(f"  {d['driverId']:20} {d['givenName']} {d['familyName']} ({d['nationality']}), DOB: {d['dateOfBirth']}")
print(f"  Total drivers in 2024: {data['MRData']['total']}")

# --- 2. Constructors ---
print("\n--- CONSTRUCTORS ---")
data = fetch("2024/constructors.json")
teams = data["MRData"]["ConstructorTable"]["Constructors"]
for t in teams:
    print(f"  {t['constructorId']:25} {t['name']} ({t['nationality']})")

# --- 3. Driver standings after final round ---
print("\n--- FINAL DRIVER STANDINGS (top 5) ---")
data = fetch("2024/driverStandings.json")
standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
for s in standings[:5]:
    d = s["Driver"]
    print(f"  P{s['position']:2} {d['code']}  {s['points']} pts  {s['wins']} wins")

# --- 4. Per-round standings (shows championship progression) ---
print("\n--- DRIVER STANDINGS AFTER ROUND 1 ---")
data = fetch("2024/1/driverStandings.json")
standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
for s in standings[:5]:
    d = s["Driver"]
    print(f"  P{s['position']:2} {d['code']}  {s['points']} pts")

# --- 5. Constructor standings ---
print("\n--- FINAL CONSTRUCTOR STANDINGS ---")
data = fetch("2024/constructorStandings.json")
standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
for s in standings:
    c = s["Constructor"]
    print(f"  P{s['position']:2} {c['name']:25} {s['points']} pts  {s['wins']} wins")

print("\n" + "=" * 60)
print("Exploration complete.")
print("=" * 60)
