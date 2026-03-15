"""
FastAPI Backend for RAN KPI Data Retrieval - Universal Query System
Performance Engineering - Telco Company

Architecture:
- Custom query templates for all use cases
- Dynamic aggregation level selection
- Flexible date/time filtering (ranges or multiple values)
- Complex KPI calculations support
- Modular and extensible
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
from enum import Enum

app = FastAPI(title="RAN KPI Data Service - Universal Query System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "local_perf",
    "user": "root",
    "password": "performance",
    "charset": "utf8mb4"
}

# ============================================================================
# REQUEST MODELS
# ============================================================================

class QueryRequest(BaseModel):
    query_category: str  # "2G", "3G", "4G", "GENERAL"
    query_subcategory: Optional[str] = None  # Vendor name (e.g., "HUAWEI", "ERICSSON")
    query_name: str  # e.g., "KPI_MONITORING"
    time_granularity: str = "DAILY"  # "HOURLY" or "DAILY"
    
    # Date/Time filters
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    multiple_date: Optional[List[str]] = None
    start_hour: Optional[int] = None
    end_hour: Optional[int] = None
    multiple_hour: Optional[List[int]] = None
    
    # Aggregation
    aggregation_level: Optional[str] = None  # e.g., "cell_name", "site_name"
    include_date: bool = True
    include_time: bool = False
    
    # KPIs to retrieve
    selected_kpis: Optional[List[str]] = None  # If None, returns all KPIs
    
    # Additional filters
    filters: Optional[Dict[str, List[str]]] = None

# ============================================================================
# DATABASE CONNECTION MANAGER
# ============================================================================

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection
        except Error as err:
            raise HTTPException(status_code=500, detail=f"Database connection error: {err}")
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute query and return results"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return results
        
        except Error as err:
            raise HTTPException(status_code=500, detail=f"Query execution error: {err}")
        
        finally:
            if cursor:
                cursor.close()

db_manager = DatabaseManager()

# ============================================================================
# QUERY CONFIGURATIONS
# ============================================================================

QUERY_CONFIG = {
    "2G": {
        "HUAWEI": {
            "KPI_MONITORING": {
                "description": "2G Huawei KPI Monitoring",
                "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],
                "parameters": [],  # Additional custom parameters
                "aggregation_levels": {
                    "cell_name": "SUBSTRING_INDEX(SUBSTRING_INDEX(sites_and_info_2g_huawei.GCELL, ',', 1), '=', -1)",
                    "site_name": "sites_and_info_2g_huawei.site",
                    "arrondissement": "sites_and_info_2g_huawei.arrondissement",
                    "commune": "sites_and_info_2g_huawei.commune",
                    "controller_name": "NE_NAME"
                },
                "time_granularities": {
                    "HOURLY": {"is_available": True, "date_field": "m.date", "time_field": "m.time"},
                    "DAILY": {"is_available": True, "date_field": "m.date", "time_field": None}
                },
                "kpi_fields": {
                    "CSSR_HUAWEI": """100 * (SUM(Suc_SDCCH_Seiz) / NULLIF(SUM(SDCCH_Seiz_Req), 0)) * 
                        (1 - (SUM(SDCCHDrop) / NULLIF(SUM(Suc_SDCCH_Seiz), 0))) * 
                        (SUM(Suc_TCH_Seiz_SG) + SUM(Suc_TCH_Seiz_TrafChann) + SUM(Suc_TCH_Seiz_handTrafChan)) / 
                        NULLIF((SUM(TCH_Seizure_Req_SC) + SUM(TCH_Seiz_Req_TrafChan) + SUM(TCH_Seiz_Req_HandTrafChan)), 0) *
                        (1 - (SUM(TCHDrop_Nume_ARCEP) / NULLIF(SUM(TCHDrop_Deno_ARCEP), 0)))""",
                    "SDCCH_Seiz": "SUM(Suc_SDCCH_Seiz)"
                },
                "sql_template": """
                    SELECT {fields}
                    FROM hourly_arcep_huawei_2g m
                    LEFT JOIN sites_and_info_2g_huawei ON sites_and_info_2g_huawei.GCELL = m.ucell
                    WHERE {where_conditions}
                    {group_by}
                    ORDER BY {order_by}
                """
            }
        },
        "ERICSSON": {
            "KPI_MONITORING": {
                "description": "2G Ericsson KPI Monitoring",
                "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],
                "parameters": [],
                "aggregation_levels": {
                    "cell_name": "m.CELL_NAME",
                    "site_name": "l.SITE_NAME",
                    "arrondissement": "l.ARRONDISSEMENT",
                    "commune": "l.COMMUNE",
                    "controller_name": "m.CONTROLLER_NAME"
                },
                "time_granularities": {
                    "HOURLY": {"is_available": True, "date_field": "m.DATE", "time_field": "m.TIME"},
                    "DAILY": {"is_available": True, "date_field": "m.DATE", "time_field": None}
                },
                "kpi_fields": {
                    "Call_Success_Rate": "AVG(ARCEP_2G_CALL_SUCCESS_RATE)",
                    "Call_Drop_Rate": "AVG(ARCEP_2G_CALL_DROP_RATE)",
                    "TCH_Congestion": "AVG(Congestion_Tch_pct)",
                    "SDCCH_Congestion": "AVG(SDCCH_Congestion_Rate)",
                    "Availability": "AVG(`2G_Availability`)"
                },
                "sql_template": """
                SELECT {fields}
                FROM kpi_2g_ericsson m
                LEFT JOIN lookup_2g_ericsson l ON m.CELL_NAME = l.CELL_NAME
                WHERE {where_conditions}
                {group_by}
                ORDER BY {order_by}
                """
            }
        }
    },
    "3G": {
        "HUAWEI": {
            "KPI_MONITORING": {
                "description": "3G Huawei KPI Monitoring",
                "date_time_filters": ["start_date", "end_date", "multiple_date"],
                "parameters": [],
                "aggregation_levels": {
                    "cell_name": "m.CELL_NAME",
                    "site_name": "l.SITE_NAME",
                    "commune": "l.COMMUNE",
                    "controller_name": "m.CONTROLLER_NAME"
                },
                "time_granularities": {
                    "DAILY": {"is_available": True, "date_field": "m.DATE", "time_field": None}
                },
                "kpi_fields": {
                    "CS_Call_Success_Rate": "AVG(VS_CSSR_3G)",
                    "PS_RAB_Success": "AVG(VS_RAB_PS_SR)"
                },
                "sql_template": """
SELECT {fields}
FROM kpi_3g_huawei m
LEFT JOIN lookup_3g_huawei l ON m.CELL_NAME = l.CELL_NAME
WHERE {where_conditions}
{group_by}
ORDER BY {order_by}
                """
            }
        }
    },
    "GENERAL": {
        "NETWORK_HEALTH": {
            "description": "General network health across all technologies",
            "date_time_filters": ["start_date", "end_date"],
            "parameters": ["technology"],
            "aggregation_levels": {
                "technology": "m.technology",
                "vendor": "m.vendor",
                "controller": "m.controller"
            },
            "time_granularities": {
                "DAILY": {"is_available": True, "date_field": "m.date", "time_field": None}
            },
            "kpi_fields": {
                "Total_Sites": "COUNT(DISTINCT site_name)",
                "Avg_Availability": "AVG(availability)"
            },
            "sql_template": """
                SELECT {fields}
                FROM network_health_summary m
                WHERE {where_conditions}
                {group_by}
                ORDER BY {order_by}
            """
        }
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_query_config(category: str, subcategory: Optional[str], query_name: str) -> Dict:
    """Get query configuration"""
    try:
        if subcategory:
            return QUERY_CONFIG[category][subcategory][query_name]
        else:
            return QUERY_CONFIG[category][query_name]
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Query not found: {category}/{subcategory}/{query_name}"
        )

def get_aggregation_hierarchy(aggregation_levels: Dict, selected_level: str) -> List[tuple]:
    """
    Get aggregation levels from selected level onwards (hierarchical filtering)
    Returns list of (display_name, sql_expression) tuples
    """
    levels_order = list(aggregation_levels.keys())
    
    if selected_level not in levels_order:
        # If no level or invalid, return all levels
        return [(name, expr) for name, expr in aggregation_levels.items()]
    
    # Get index of selected level
    start_index = levels_order.index(selected_level)
    
    # Return from selected level onwards
    return [(name, aggregation_levels[name]) for name in levels_order[start_index:]]

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {
        "status": "RAN KPI Data Service - Universal Query System",
        "version": "3.0",
        "database": "MySQL"
    }

@app.get("/api/query-categories")
def get_query_categories():
    """Get all query categories (2G, 3G, 4G, GENERAL)"""
    return {
        "categories": list(QUERY_CONFIG.keys())
    }

@app.get("/api/query-subcategories/{category}")
def get_query_subcategories(category: str):
    """Get subcategories for a category (e.g., vendors for 2G)"""
    if category not in QUERY_CONFIG:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    config = QUERY_CONFIG[category]
    
    # Check if this has subcategories (vendors) or direct queries
    first_key = next(iter(config.keys()))
    if isinstance(config[first_key], dict) and "description" in config[first_key]:
        # Direct queries (like GENERAL)
        return {
            "category": category,
            "has_subcategories": False,
            "queries": list(config.keys())
        }
    else:
        # Has subcategories (like 2G -> HUAWEI, ERICSSON)
        return {
            "category": category,
            "has_subcategories": True,
            "subcategories": list(config.keys())
        }

@app.get("/api/queries/{category}")
def get_queries_in_category(category: str, subcategory: Optional[str] = None):
    """Get available queries in a category/subcategory"""
    try:
        if subcategory:
            queries = QUERY_CONFIG[category][subcategory]
        else:
            queries = QUERY_CONFIG[category]
        
        return {
            "category": category,
            "subcategory": subcategory,
            "queries": [
                {
                    "name": name,
                    "description": config["description"]
                }
                for name, config in queries.items()
            ]
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Category/subcategory not found")

@app.get("/api/query-details/{category}/{query_name}")
def get_query_details(category: str, query_name: str, subcategory: Optional[str] = None):
    """Get detailed information about a specific query"""
    config = get_query_config(category, subcategory, query_name)
    
    return {
        "category": category,
        "subcategory": subcategory,
        "query_name": query_name,
        "description": config["description"],
        "date_time_filters": config["date_time_filters"],
        "aggregation_levels": list(config["aggregation_levels"].keys()),
        "available_kpis": list(config["kpi_fields"].keys()),
        "time_granularities": list(config["time_granularities"].keys())
    }

@app.post("/api/data/query")
def execute_query(request: QueryRequest):
    """Execute a query with dynamic parameters"""
    try:
        # Get query configuration
        config = get_query_config(
            request.query_category,
            request.query_subcategory,
            request.query_name
        )
        
        # Build SQL query
        sql_query = build_dynamic_query(request, config)
        
        # Execute query
        results = db_manager.execute_query(sql_query)
        
        return {
            "success": True,
            "query_category": request.query_category,
            "query_subcategory": request.query_subcategory,
            "query_name": request.query_name,
            "row_count": len(results),
            "data": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    """Check database connection health"""
    try:
        db_manager.connect()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ============================================================================
# DYNAMIC SQL QUERY BUILDER
# ============================================================================

def build_dynamic_query(request: QueryRequest, config: Dict) -> str:
    """Build SQL query dynamically based on request and configuration"""
    
    # Get the SQL template
    sql_template = config["sql_template"]
    
    # 1. Build SELECT fields
    select_fields = build_select_fields(request, config)
    
    # 2. Build WHERE conditions
    where_conditions = build_where_clause(request, config)
    
    # 3. Build GROUP BY clause
    group_by_clause = build_group_by_clause(request, config)
    
    # 4. Build ORDER BY clause
    order_by_clause = build_order_by(request, config)
    
    # 5. Replace placeholders in SQL template
    sql_query = sql_template.format(
        fields=select_fields,
        where_conditions=where_conditions if where_conditions else "1=1",
        group_by=group_by_clause,
        order_by=order_by_clause
    )
    
    return sql_query.strip()

def build_select_fields(request: QueryRequest, config: Dict) -> str:
    """Build SELECT field list dynamically"""
    fields = []
    
    # Get time granularity config
    time_config = config["time_granularities"].get(request.time_granularity, {})
    date_field = time_config.get("date_field")
    time_field = time_config.get("time_field")
    
    # 1. Add date field if requested
    if request.include_date and date_field:
        fields.append(f"{date_field} AS date")
    
    # 2. Add time field if requested and available
    if request.include_time and time_field:
        fields.append(f"{time_field} AS time")
    
    # 3. Add aggregation level fields (hierarchical)
    if request.aggregation_level:
        agg_hierarchy = get_aggregation_hierarchy(
            config["aggregation_levels"],
            request.aggregation_level
        )
        for level_name, level_expr in agg_hierarchy:
            fields.append(f"{level_expr} AS {level_name}")
    
    # 4. Add selected KPI fields
    kpi_fields = config["kpi_fields"]
    if request.selected_kpis:
        for kpi in request.selected_kpis:
            if kpi in kpi_fields:
                fields.append(f"{kpi_fields[kpi]} AS {kpi}")
    else:
        # Add all KPIs if none selected
        for kpi_name, kpi_expr in kpi_fields.items():
            fields.append(f"{kpi_expr} AS {kpi_name}")
    
    return ",\n    ".join(fields)


def build_where_clause(request: QueryRequest, config: Dict) -> str:
    """Build WHERE conditions with date/time and additional filters"""
    conditions = []
    
    # Get time granularity config
    time_config = config["time_granularities"].get(request.time_granularity, {})
    date_field = time_config.get("date_field")
    time_field = time_config.get("time_field")
    
    # Date filters
    if date_field:
        if request.multiple_date:
            # Multiple specific dates
            dates_str = "', '".join(request.multiple_date)
            conditions.append(f"{date_field} IN ('{dates_str}')")
        elif request.start_date or request.end_date:
            # Date range
            if request.start_date:
                conditions.append(f"{date_field} >= '{request.start_date}'")
            if request.end_date:
                conditions.append(f"{date_field} <= '{request.end_date}'")
    
    # Time/Hour filters (if time field exists)
    if time_field:
        if request.multiple_hour:
            # Multiple specific hours
            hours_str = ", ".join(map(str, request.multiple_hour))
            conditions.append(f"HOUR({time_field}) IN ({hours_str})")
        elif request.start_hour is not None or request.end_hour is not None:
            # Hour range
            if request.start_hour is not None:
                conditions.append(f"HOUR({time_field}) >= {request.start_hour}")
            if request.end_hour is not None:
                conditions.append(f"HOUR({time_field}) <= {request.end_hour}")
    
    # Additional filters
    if request.filters:
        for filter_key, filter_values in request.filters.items():
            if filter_values:
                # Find the filter column in aggregation levels or use as-is
                agg_levels = config["aggregation_levels"]
                if filter_key in agg_levels:
                    filter_column = agg_levels[filter_key]
                else:
                    filter_column = filter_key
                
                escaped_values = [val.replace("'", "''") for val in filter_values]
                values_str = "', '".join(escaped_values)
                conditions.append(f"{filter_column} IN ('{values_str}')")
    
    if conditions:
        return "\n    AND ".join(conditions)
    return "1=1"  # Return default condition if no filters

def build_group_by_clause(request: QueryRequest, config: Dict) -> str:
    """Build GROUP BY clause matching SELECT fields"""
    group_fields = []
    
    # Get time granularity config
    time_config = config["time_granularities"].get(request.time_granularity, {})
    date_field = time_config.get("date_field")
    time_field = time_config.get("time_field")
    
    # 1. Add date field if included
    if request.include_date and date_field:
        group_fields.append(date_field)
    
    # 2. Add time field if included
    if request.include_time and time_field:
        group_fields.append(time_field)
    
    # 3. Add aggregation level fields (hierarchical)
    if request.aggregation_level:
        agg_hierarchy = get_aggregation_hierarchy(
            config["aggregation_levels"],
            request.aggregation_level
        )
        for level_name, level_expr in agg_hierarchy:
            group_fields.append(level_expr)
    
    # Only add GROUP BY if we have aggregation or date/time grouping with KPIs
    if group_fields and config["kpi_fields"]:
        return "GROUP BY " + ", ".join(group_fields)
    
    return ""

def build_order_by(request: QueryRequest, config: Dict) -> str:
    """Build ORDER BY clause"""
    order_fields = []
    
    # Get time granularity config
    time_config = config["time_granularities"].get(request.time_granularity, {})
    date_field = time_config.get("date_field")
    time_field = time_config.get("time_field")
    
    if request.include_date and date_field:
        order_fields.append(date_field)
    
    if request.include_time and time_field:
        order_fields.append(time_field)
    
    if not order_fields:
        order_fields.append("1")  # Order by first column
    
    return ", ".join(order_fields)

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("RAN KPI Data Service - Universal Query System")
    print("=" * 70)
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Query Categories: {list(QUERY_CONFIG.keys())}")
    print("=" * 70)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)