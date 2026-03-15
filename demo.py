import requests
import json

# API endpoint
url = "http://localhost:8000/api/data/query"

# Request payload
payload = {
    "query_category": "2G",
    "query_subcategory": "HUAWEI",
    "query_name": "KPI_MONITORING",
    "time_granularity": "HOURLY",
    "start_date": "2025-11-20",
    "end_date": "2025-11-20",
    "include_date": True,
    "aggregation_level": "site_name",
    "selected_kpis": ["CSSR_HUAWEI"]
}

# Make the request
try:
    response = requests.post(url, json=payload)
    
    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        
        print("✓ Query executed successfully!")
        print(f"Row count: {data['row_count']}")
        print("\nData:")
        print(json.dumps(data['data'], indent=2))
        
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.json())
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API. Make sure the server is running on port 8000")
except Exception as e:
    print(f"✗ Error: {e}")