"""
API client — tests /main_kpis_availability
Run the server first:  python app.py
"""

import requests
import json

BASE_URL = "http://localhost:8001"


def pretty(data):
    print(json.dumps(data, indent=2, default=str))


def check_health():
    r = requests.get(f"{BASE_URL}/health")
    print("=== HEALTH ===")
    pretty(r.json())
    print()


def fetch_kpis(**params):
    r = requests.get(f"{BASE_URL}/main_kpis_availability", params=params)
    return r.json()


if __name__ == "__main__":

    check_health()

    # --- Test 1: DAILY, no aggregation → separate 2G/3G/4G -------
    print("=" * 60)
    print("TEST 1 — DAILY | no aggregation")
    print("=" * 60)
    result = fetch_kpis(
        start_date="2026-02-20",
        end_date="2026-02-20",
        time_granularity="HOURLY",
         aggregation_level="",
    )
    print(f"success : {result['success']}")
    print(f"errors  : {result['errors']}")
    for tech in ["2G", "3G", "4G"]:
        rows = result["data"].get(tech, [])
        print(f"  {tech}: {len(rows)} rows  |  cols: {list(rows[0].keys()) if rows else '[]'}")
    print()

    # --- Test 2: DAILY + commune aggregation → merged flat list ---
    # print("=" * 60)
    # print("TEST 2 — DAILY | aggregation_level=commune")
    # print("=" * 60)
    # result = fetch_kpis(
    #     start_date="2025-01-01",
    #     end_date="2025-01-07",
    #     time_granularity="DAILY",
    #     aggregation_level="commune",
    # )
    # print(f"success : {result['success']}")
    # print(f"errors  : {result['errors']}")
    # rows = result["data"]
    # print(f"  rows : {len(rows)}")
    # if rows:
    #     print(f"  cols : {list(rows[0].keys())}")
    #     print("  first row:")
    #     pretty(rows[0])
    # print()

    # --- Test 3: MONTHLY, no aggregation -------------------------
    # print("=" * 60)
    # print("TEST 3 — MONTHLY | no aggregation")
    # print("=" * 60)
    # result = fetch_kpis(
    #     start_date="2025-01-01",
    #     end_date="2025-06-30",
    #     time_granularity="MONTHLY",
    # )
    # print(f"success : {result['success']}")
    # print(f"errors  : {result['errors']}")
    # for tech in ["2G", "3G", "4G"]:
    #     rows = result["data"].get(tech, [])
    #     print(f"  {tech}: {len(rows)} rows")
    # print()

    # --- Test 4: HOURLY + commune --------------------------------
    print("=" * 60)
    print("TEST 4 — HOURLY | aggregation_level=commune")
    print("=" * 60)
    result = fetch_kpis(
          start_date="2026-02-20",
        end_date="2026-02-20",
        time_granularity="HOURLY",
        aggregation_level="COMMUNE",
    )
    print(f"success : {result['success']}")
    print(f"errors  : {result['errors']}")
    rows = result["data"]
    print(f"  rows : {len(rows)}")
    if rows:
        print("  first row:")
        print(rows[0])