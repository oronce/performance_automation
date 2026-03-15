"""
Python HTTP Client Examples for RAN KPI Data Service API
"""

import requests
import json
from datetime import date, timedelta

# Base URL of your API
BASE_URL = "http://localhost:8000"

# ============================================================================
# EXAMPLE 1: Health Check
# ============================================================================

def health_check():
    """Check if API is healthy"""
    response = requests.get(f"{BASE_URL}/api/health")
    print("Health Check:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# EXAMPLE 2: Get Available Technologies
# ============================================================================

def get_technologies():
    """Get all available technologies (2G, 3G, 4G)"""
    response = requests.get(f"{BASE_URL}/api/technologies")
    print("....Available Technologies:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# EXAMPLE 3: Get Vendors for a Technology
# ============================================================================

def get_vendors(tech_type="2G"):
    """Get vendors for a technology"""
    response = requests.get(f"{BASE_URL}/api/vendors/{tech_type}")
    print(f"Vendors for {tech_type}:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# EXAMPLE 4: Get KPI Groups
# ============================================================================

def get_kpi_groups(tech_type="2G", vendor="ERICSSON"):
    """Get available KPI groups"""
    response = requests.get(f"{BASE_URL}/api/kpi-groups/{tech_type}/{vendor}")
    print(f"KPI Groups for {tech_type}/{vendor}:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# EXAMPLE 5: Get Available KPIs
# ============================================================================

def get_kpis(tech_type="2G", vendor="ERICSSON", kpi_group="ALL_KPIS"):
    """Get available KPIs for a specific group"""
    response = requests.get(f"{BASE_URL}/api/kpis/{tech_type}/{vendor}/{kpi_group}")
    print(f"KPIs for {tech_type}/{vendor}/{kpi_group}:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# EXAMPLE 6: Get Filter Values (e.g., all cities/communes)
# ============================================================================

def get_filter_values(tech_type="2G", vendor="ERICSSON", filter_type="commune"):
    """Get all available values for a filter"""
    response = requests.get(f"{BASE_URL}/api/filters/{tech_type}/{vendor}/{filter_type}")
    print(f"Filter values for {filter_type}:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# EXAMPLE 7: Main Query - Get KPI Data
# ============================================================================

def query_kpi_data():
    """Query KPI data with filters"""

    # Calculate date range (last 7 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    # Build request payload - NEW API FORMAT
    payload = {
        "query_category": "2G",
        "query_subcategory": "HUAWEI",
        "query_name": "KPI_MONITORING2",
        "time_granularity": "HOURLY",
        "aggregation_level": "controller_name",
        "selected_kpis": ["CSSR_HUAWEI", "CBR_HUAWEI","CDR_HUAWEI"],
        "include_date": True,
        "include_time": True,
        "start_date": '2025-11-20',
        "end_date": '2025-12-23',
        #"start_hour": 0,
        #"end_hour": 23,
        #"filters": {"cell_name": ["BRIGN3"]}  # Example filter
    }

    print("Querying KPI Data:")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload)

    if response.status_code == 200:
        result = response.json()
        print(f"Success! Got {result['row_count']} rows")
        print(json.dumps(result, indent=2))
        import pandas as pd
        df = pd.DataFrame(result['data'])
        df.to_excel("excel_output/graph_test.xlsx")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

    print()

# ============================================================================
# EXAMPLE 8: Cell-Level Data Query
# ============================================================================

def query_cell_level_data():
    """Query data at cell level (not aggregated)"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=1)
    
    payload = {
        "tech_type": "4G",
        "vendor": "HUAWEI",
        "kpi_group": "DATA_PERFORMANCE",
        "aggregation_level": "CELL_NAME",
        "time_granularity": "HOURLY",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "start_hour": 9,
        "end_hour": 17,
        "selected_kpis": ["DL_Throughput", "UL_Throughput"]
    }
    
    print("Querying Cell-Level Data (Hourly):")
    response = requests.post(f"{BASE_URL}/api/data/query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Got {result['row_count']} rows")
        # Print first few rows
        if result['data']:
            print("First row:")
            print(json.dumps(result['data'][0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()

# ============================================================================
# EXAMPLE 9: Custom Queries
# ============================================================================

def list_custom_queries():
    """List all available custom queries"""
    response = requests.get(f"{BASE_URL}/api/custom-queries")
    print("Available Custom Queries:")
    print(json.dumps(response.json(), indent=2))
    print()

def execute_custom_query():
    """Execute a custom query"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    payload = {
        "query_name": "TOP_WORST_CELLS",
        "parameters": {
            "tech_type": "3G",
            "vendor": "ERICSSON",
            "kpi_name": "Call_Success_Rate",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "limit": 20,
            "sort_order": "ASC"
        }
    }
    
    print("Executing Custom Query (TOP_WORST_CELLS):")
    response = requests.post(f"{BASE_URL}/api/data/custom-query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Got {result['row_count']} rows")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()

# ============================================================================
# EXAMPLE 10: View Configuration
# ============================================================================

def view_config(tech_type="2G", vendor="ERICSSON", kpi_group="ALL_KPIS"):
    """View the complete configuration (for debugging)"""
    response = requests.get(f"{BASE_URL}/api/config/view/{tech_type}/{vendor}/{kpi_group}")
    print("Configuration:")
    print(json.dumps(response.json(), indent=2))
    print()

# ============================================================================
# USING REQUESTS SESSION (for multiple requests)
# ============================================================================

def use_session():
    """Use requests Session for better performance with multiple requests"""
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # First request
    resp1 = session.get(f"{BASE_URL}/api/technologies")
    print("Technologies from session:")
    print(json.dumps(resp1.json(), indent=2))
    
    # Second request (reuses connection)
    resp2 = session.get(f"{BASE_URL}/api/vendors/2G")
    print("\nVendors from session:")
    print(json.dumps(resp2.json(), indent=2))
    
    session.close()
    print()

# ============================================================================
# USING URLLIB (Alternative to requests)
# ============================================================================

def use_urllib():
    """Alternative using built-in urllib (no external dependency)"""
    
    import urllib.request
    import urllib.parse
    
    # GET request
    url = f"{BASE_URL}/api/technologies"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        print("Using urllib - Technologies:")
        print(json.dumps(data, indent=2))
    
    # POST request
    url = f"{BASE_URL}/api/data/query"
    end_date = date.today()
    start_date = end_date - timedelta(days=1)
    
    payload = {
        "tech_type": "2G",
        "vendor": "ERICSSON",
        "kpi_group": "VOICE_QUALITY",
        "aggregation_level": "COMMUNE",
        "time_granularity": "DAILY",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "selected_kpis": ["Call_Success_Rate"]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print("\nUsing urllib - Query result:")
            print(json.dumps(data, indent=2))
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.reason}")
    print()

# ============================================================================
# ERROR HANDLING
# ============================================================================

def handle_errors():
    """Example of error handling"""
    
    try:
        # Invalid technology
        response = requests.get(f"{BASE_URL}/api/vendors/5G")
        response.raise_for_status()  # Raise HTTPError for bad status
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Details: {e.response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    print()

# ============================================================================
# EXAMPLE 11: Multi-CTE Combined Query (HUAWEI + ERICSSON)
# ============================================================================

def query_combined_network_kpi():
    """Query combined network KPI from multiple vendors using multi-CTE"""

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    # Test DAILY granularity
    payload_daily = {
        "query_category": "2G_NETWORK",
        "query_subcategory": "COMBINED",
        "query_name": "KPI_MONITORING",
        "time_granularity": "DAILY",
        "aggregation_level": None,
        "selected_kpis": ["CSSR_HUAWEI", "CSSR_ERICSSON", "CSSR_NETWORK", "CDR_NETWORK", "CBR_NETWORK"],
        "include_date": True,
        "include_time": False,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "filters": {}
    }

    print("Querying Combined Network KPI (DAILY):")
    print(f"Payload: {json.dumps(payload_daily, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_daily)

    if response.status_code == 200:
        result = response.json()
        print(f"Success! Got {result['row_count']} rows")
        print(f"Query Type: {result.get('query_type')}")
        if result.get('data'):
            print("First row:")
            print(json.dumps(result['data'][0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    print()

    # Test WEEKLY granularity
    payload_weekly = payload_daily.copy()
    payload_weekly["time_granularity"] = "WEEKLY"

    print("Querying Combined Network KPI (WEEKLY):")
    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_weekly)

    if response.status_code == 200:
        result = response.json()
        print(f"Success! Got {result['row_count']} rows")
        if result.get('data'):
            print("First row:")
            print(json.dumps(result['data'][0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    print()

    # Test MONTHLY granularity
    payload_monthly = payload_daily.copy()
    payload_monthly["time_granularity"] = "MONTHLY"

    print("Querying Combined Network KPI (MONTHLY):")
    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_monthly)

    if response.status_code == 200:
        result = response.json()
        print(f"Success! Got {result['row_count']} rows")
        if result.get('data'):
            print("First row:")
            print(json.dumps(result['data'][0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    print()

# ============================================================================
# EXAMPLE 12: Test RAW_SQL Query Type (NEW)
# ============================================================================

def test_raw_sql_query():
    """Test the new raw_sql query type with source-based placeholders"""

    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    print("test hourly first")
    # Test HOURLY granularity
    payload_hourly = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "HOURLY",
        "aggregation_level": None,  # Try: None, "cell_name", "site_name", "commune"
        "selected_kpis": [],  # Not used in raw_sql, but can be passed
        "include_date": True,
        "include_time": True,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "start_hour": 8,
        "end_hour": 20,
        "filters": {}
    }

    print("=" * 70)
    print("Testing RAW_SQL Query Type - HOURLY")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_hourly, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_hourly)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"Row Count: {result['row_count']}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    #     if result.get('data'):
    #         print("\nFirst row:")
    #         print(json.dumps(result['data'][0], indent=2))
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # Test DAILY granularity
    payload_daily = payload_hourly.copy()
    payload_daily["time_granularity"] = "DAILY"
    payload_daily["include_time"] = False
    payload_daily.pop("start_hour", None)
    payload_daily.pop("end_hour", None)

    print("=" * 70)
    print("Testing RAW_SQL Query Type - DAILY")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_daily, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_daily)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"Row Count: {result['row_count']}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # Test WEEKLY granularity
    payload_weekly = payload_daily.copy()
    payload_weekly["time_granularity"] = "WEEKLY"

    print("=" * 70)
    print("Testing RAW_SQL Query Type - WEEKLY")
    print("=" * 70)

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_weekly)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # Test with aggregation
    payload_with_agg = payload_daily.copy()
    payload_with_agg["aggregation_level"] = "cell_name"

    print("=" * 70)
    print("Testing RAW_SQL Query Type - DAILY with cell_name aggregation")
    print("=" * 70)

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_with_agg)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test with MULTIPLE DATES (instead of start_date/end_date)
    # =========================================================================
    payload_multiple_dates = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "DAILY",
        "aggregation_level": None,
        "selected_kpis": [],
        "include_date": True,
        "include_time": False,
        "multiple_date": ["2025-01-15", "2025-01-20", "2025-01-25"],  # Specific dates
        "filters": {}
    }

    print("=" * 70)
    print("Testing RAW_SQL - MULTIPLE DATES")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_multiple_dates, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_multiple_dates)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test with MULTIPLE HOURS (instead of start_hour/end_hour)
    # =========================================================================
    payload_multiple_hours = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "HOURLY",
        "aggregation_level": None,
        "selected_kpis": [],
        "include_date": True,
        "include_time": True,
        "start_date": (date.today() - timedelta(days=3)).isoformat(),
        "end_date": date.today().isoformat(),
        "multiple_hour": [8, 12, 14, 18, 20],  # Specific hours only
        "filters": {}
    }

    print("=" * 70)
    print("Testing RAW_SQL - MULTIPLE HOURS")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_multiple_hours, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_multiple_hours)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test with FILTERS (e.g., filter by cell_name)
    # =========================================================================
    payload_with_filters = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "DAILY",
        "aggregation_level": "cell_name",
        "selected_kpis": [],
        "include_date": True,
        "include_time": False,
        "start_date": (date.today() - timedelta(days=7)).isoformat(),
        "end_date": date.today().isoformat(),
        "filters": {
            "cell_name": ["CELL_001", "CELL_002", "CELL_003"]  # Filter specific cells
        }
    }

    print("=" * 70)
    print("Testing RAW_SQL - WITH FILTERS (cell_name)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_with_filters, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_with_filters)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test COMBO: Multiple dates + Multiple hours + Filters
    # =========================================================================
    payload_combo = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "HOURLY",
        "aggregation_level": "site_name",
        "selected_kpis": [],
        "include_date": True,
        "include_time": True,
        "multiple_date": ["2025-01-20", "2025-01-21", "2025-01-22"],
        "multiple_hour": [9, 10, 11, 12],
        "filters": {
            "site_name": ["SITE_A", "SITE_B"]
        }
    }

    print("=" * 70)
    print("Testing RAW_SQL - COMBO (multiple_date + multiple_hour + filters)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_combo, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_combo)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test with NOT_IN_FILTERS (exclude specific values)
    # =========================================================================
    payload_not_in = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "DAILY",
        "aggregation_level": "cell_name",
        "selected_kpis": [],
        "include_date": True,
        "include_time": False,
        "start_date": (date.today() - timedelta(days=7)).isoformat(),
        "end_date": date.today().isoformat(),
        "not_in_filters": {
            "cell_name": ["BAD_CELL_001", "BAD_CELL_002", "TEST_CELL"]  # Exclude these cells
        }
    }

    print("=" * 70)
    print("Testing RAW_SQL - NOT_IN_FILTERS (exclude cells)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_not_in, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_not_in)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test BOTH filters and not_in_filters together
    # =========================================================================
    payload_both_filters = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "DAILY",
        "aggregation_level": "cell_name",
        "selected_kpis": [],
        "include_date": True,
        "include_time": False,
        "start_date": (date.today() - timedelta(days=7)).isoformat(),
        "end_date": date.today().isoformat(),
        "filters": {
            "commune": ["COMMUNE_A", "COMMUNE_B"]  # Include only these communes
        },
        "not_in_filters": {
            "cell_name": ["BAD_CELL_001", "TEST_CELL"]  # But exclude these cells
        }
    }

    print("=" * 70)
    print("Testing RAW_SQL - BOTH filters + not_in_filters")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_both_filters, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_both_filters)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test DYNAMIC JOIN ON - HOURLY (should include time in JOIN condition)
    # =========================================================================
    payload_join_hourly = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "HOURLY",
        "aggregation_level": None,  # No aggregation - join only on date + time
        "selected_kpis": [],
        "include_date": True,
        "include_time": True,
        "start_date": (date.today() - timedelta(days=3)).isoformat(),
        "end_date": date.today().isoformat(),
        "start_hour": 8,
        "end_hour": 20,
        "filters": {}
    }

    print("=" * 70)
    print("Testing DYNAMIC JOIN - HOURLY (join on date + time)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_join_hourly, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_join_hourly)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test DYNAMIC JOIN ON - DAILY (should NOT include time in JOIN condition)
    # =========================================================================
    payload_join_daily = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "DAILY",
        "aggregation_level": None,  # No aggregation - join only on date
        "selected_kpis": [],
        "include_date": True,
        "include_time": False,
        "start_date": (date.today() - timedelta(days=7)).isoformat(),
        "end_date": date.today().isoformat(),
        "filters": {}
    }

    print("=" * 70)
    print("Testing DYNAMIC JOIN - DAILY (join on date only)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_join_daily, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_join_daily)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test DYNAMIC JOIN ON - HOURLY with AGGREGATION (join on date + time + agg)
    # =========================================================================
    payload_join_hourly_agg = {
        "query_category": "TEST_RAW_SQL",
        "query_subcategory": "SAMPLE",
        "query_name": "KPI_TEST",
        "time_granularity": "HOURLY",
        "aggregation_level": "cell_name",  # Aggregation - join includes cell_name
        "selected_kpis": [],
        "include_date": True,
        "include_time": True,
        "start_date": (date.today() - timedelta(days=3)).isoformat(),
        "end_date": date.today().isoformat(),
        "start_hour": 8,
        "end_hour": 20,
        "filters": {}
    }

    print("=" * 70)
    print("Testing DYNAMIC JOIN - HOURLY + cell_name (join on date + time + cell)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_join_hourly_agg, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_join_hourly_agg)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()

    # =========================================================================
    # Test DYNAMIC JOIN ON - DAILY with AGGREGATION (join on date + agg)
    # =========================================================================
    payload_join_daily_agg = {
        "query_category": "3G",
        "query_subcategory": "COMBINED",
        "query_name": "NETWORK",
        "time_granularity": "HOURLY",
        "aggregation_level": None,  # Aggregation - join includes commune
        "selected_kpis": [],
        "include_date": True,
        "include_time": True,
        #"start_date": (date.today() - timedelta(days=1)).isoformat(),
        "start_date": (date.today() - timedelta(days=1)).isoformat(),
        "end_date": (date.today() - timedelta(days=1)).isoformat(),
        #"end_date": date.today().isoformat(),
        "filters": {}
    }

    print("=" * 70)
    print("Testing DYNAMIC JOIN - DAILY + commune (join on date + commune)")
    print("=" * 70)
    print(f"Payload: {json.dumps(payload_join_daily_agg, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/data/query", json=payload_join_daily_agg)

    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"\nSuccess! Query Type: {result.get('query_type')}")
    #     print(f"\nGenerated SQL:\n{result.get('query', 'N/A')}")
    # else:
    #     print(f"\nError: {response.status_code}")
    #     print(response.json())
    # print()


def get_raw_sql_query_details():
    """Get query details for raw_sql query type"""

    print("=" * 70)
    print("Getting RAW_SQL Query Details")
    print("=" * 70)

    response = requests.get(
        f"{BASE_URL}/api/query-details/TEST_RAW_SQL/KPI_TEST",
        params={"subcategory": "SAMPLE"}
    )

    # if response.status_code == 200:
    #     result = response.json()
    #     print(json.dumps(result, indent=2))
    # else:
    #     print(f"Error: {response.status_code}")
    #     print(response.json())
    # print()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RAN KPI API - Python Client Examples")
    print("=" * 70)
    print()

    try:
        # Run examples
        # health_check()
        # get_technologies()
        # get_vendors("2G")
        # get_kpi_groups("2G", "ERICSSON")
        # get_kpis("2G", "ERICSSON", "VOICE_QUALITY")
        # get_filter_values("2G", "ERICSSON", "commune")
        # query_kpi_data()
        # query_cell_level_data()
        # list_custom_queries()
        # execute_custom_query()
        # view_config("2G", "ERICSSON", "ALL_KPIS")
        # use_session()

        # NEW: Test multi-CTE combined query
        # query_combined_network_kpi()

        # NEW: Test raw_sql query type
        get_raw_sql_query_details()
        test_raw_sql_query()

        # Uncomment to use urllib instead of requests
        # use_urllib()

        # Error handling example
        # handle_errors()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
