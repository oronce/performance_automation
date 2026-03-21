# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DB_CONFIG = {
    'host': '10.22.33.116',
    'user': 'root',
    'password': 'performance',
    'database': 'performanceroute'  # <-- CHANGE THIS to your database name
}

# =============================================================================
# DATE LIMITS
# =============================================================================
MAX_DAYS_ALLOWED = 10
DEFAULT_DAYS = 2

# =============================================================================
# KPI CHART GROUPINGS
# Edit this to control which KPIs appear in which chart
# Each key is the chart title, value is dict with "columns" and optional "threshold"
# =============================================================================
KPI_CHART_GROUPS = {
    "CSSR (%)": {
        "columns": ["CSSR_HUAWEI", "CSSR_ERICSSON", "CSSR_NETWORK"],
        "threshold": 99
    },
    "CDR (%)": {
        "columns": ["CDR_HUAWEI", "CDR_ERICSSON", "CDR_NETWORK"],
        "threshold": 2
    },
    "CBR (%)": {
        "columns": ["CBR_HUAWEI", "CBR_ERICSSON", "CBR_NETWORK"],
        "threshold": 1
    },
    "TCH Congestion Rate (%)": {
        "columns": ["TCH_CONGESTION_RATE_HUAWEI", "TCH_CONGESTION_RATE_ERICSSON", "TCH_CONGESTION_RATE_NETWORK"],
        "threshold": None
    },
    "SDCCH Congestion Rate (%)": {
        "columns": ["SDCCH_CONGESTION_RATE_HUAWEI", "SDCCH_CONGESTION_RATE_ERICSSON", "SDCCH_CONGESTION_RATE_NETWORK"],
        "threshold": None
    },
    "SDCCH Drop Rate (%)": {
        "columns": ["SDCCH_DROP_RATE_HUAWEI", "SDCCH_DROP_RATE_ERICSSON", "SDCCH_DROP_RATE_NETWORK"],
        "threshold": None
    },
    "Cell Availability Rate (%)": {
        "columns": ["CELL_AVAILABILITY_RATE_HUAWEI", "CELL_AVAILABILITY_RATE_ERICSSON", "CELL_AVAILABILITY_RATE_NETWORK"],
        "threshold": 99
    },
    "Traffic Voice (Erlang)": {
        "columns": ["TRAFFIC_VOIX_HUAWEI", "TRAFFIC_VOIX_ERICSSON", "TRAFFIC_NETWORK"],
        "threshold": None
    },
    "Handover Success Rate (%)": {
        "columns": ["HANDOVER_SUCCESS_RATE_HUAWEI"],
        "threshold": None
    }
}

# =============================================================================
# CHART COLORS
# Colors for each series in a chart (HUAWEI, ERICSSON, NETWORK)
# =============================================================================
CHART_COLORS = [
    "#e74c3c",  # Red - HUAWEI
    "#3498db",  # Blue - ERICSSON
    "#2ecc71",  # Green - NETWORK
    "#f39c12",  # Orange
    "#9b59b6",  # Purple
]