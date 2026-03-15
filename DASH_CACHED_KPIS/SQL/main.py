"""
Standalone SQL generator — raw_sql query type only.
Imports QUERY_CONFIG from contants.py, builds and returns final SQL string.
No FastAPI or DB dependency.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from contants import QUERY_CONFIG


# ============================================================================
# GRANULARITY TRANSFORMS
# ============================================================================

GRANULARITY_TRANSFORMS = {
    "HOURLY": {
        "date_transform": "{col}",
        "time_transform": "{col}",
        "include_time": True
    },
    "DAILY": {
        "date_transform": "{col}",
        "time_transform": None,
        "include_time": False
    },
    "WEEKLY": {
        "date_transform": "YEARWEEK({col}, 1)",
        "time_transform": None,
        "include_time": False
    },
    "MONTHLY": {
        "date_transform": "DATE_FORMAT({col}, '%Y-%m')",
        "time_transform": None,
        "include_time": False
    }
}


# ============================================================================
# REQUEST MODEL (plain dataclass — no Pydantic/FastAPI needed)
# ============================================================================

@dataclass
class QueryRequest:
    query_category: str
    query_name: str
    time_granularity: str = "DAILY"
    query_subcategory: Optional[str] = None

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    multiple_date: Optional[List[str]] = None
    start_hour: Optional[int] = None
    end_hour: Optional[int] = None
    multiple_hour: Optional[List[int]] = None

    aggregation_level: Optional[str] = None
    include_date: bool = True
    include_time: bool = False

    selected_kpis: Optional[List[str]] = None
    filters: Optional[Dict[str, List[str]]] = None
    not_in_filters: Optional[Dict[str, List[str]]] = None


# ============================================================================
# CONFIG LOOKUP
# ============================================================================

def get_query_config(category: str, subcategory: Optional[str], query_name: str) -> Dict:
    try:
        if subcategory:
            return QUERY_CONFIG[category][subcategory][query_name]
        else:
            return QUERY_CONFIG[category][query_name]
    except KeyError:
        raise ValueError(f"Query not found: {category}/{subcategory}/{query_name}")


# ============================================================================
# PLACEHOLDER BUILDERS
# ============================================================================

def _build_source_placeholders(
    source_name: str,
    source_config: Dict,
    request: QueryRequest,
    transform_config: Dict,
    include_time: bool
) -> Dict[str, str]:
    """Build all placeholder values for a single source."""

    placeholders = {}

    date_col = source_config.get("date_col")
    time_col = source_config.get("time_col")
    aggregations = source_config.get("aggregations", {})

    date_transform = transform_config["date_transform"]
    transformed_date = date_transform.format(col=date_col) if date_col else ""
    transformed_time = time_col if include_time and time_col else ""

    agg_col = ""
    if request.aggregation_level and request.aggregation_level in aggregations:
        agg_col = aggregations[request.aggregation_level]

    placeholders[f"{source_name}__date"] = transformed_date
    placeholders[f"{source_name}__time"] = transformed_time
    placeholders[f"{source_name}__aggregation"] = agg_col

    # {source__select_fields}
    select_parts = []
    if request.include_date and transformed_date:
        select_parts.append(f"{transformed_date} AS date")
    if request.include_time and transformed_time:
        select_parts.append(f"{transformed_time} AS time")
    if agg_col:
        select_parts.append(f"{agg_col} AS {request.aggregation_level}")
    placeholders[f"{source_name}__select_fields"] = ", ".join(select_parts) if select_parts else "1"

    # {source__where_clause}
    where_parts = []
    if date_col:
        if request.multiple_date:
            dates_str = "', '".join(request.multiple_date)
            where_parts.append(f"{date_col} IN ('{dates_str}')")
        else:
            if request.start_date:
                where_parts.append(f"{date_col} >= '{request.start_date}'")
            if request.end_date:
                where_parts.append(f"{date_col} <= '{request.end_date}'")

    if include_time and time_col:
        if request.multiple_hour:
            hours_str = ", ".join(map(str, request.multiple_hour))
            where_parts.append(f"HOUR({time_col}) IN ({hours_str})")
        else:
            if request.start_hour is not None:
                where_parts.append(f"HOUR({time_col}) >= {request.start_hour}")
            if request.end_hour is not None:
                where_parts.append(f"HOUR({time_col}) <= {request.end_hour}")

    if request.filters:
        for filter_key, filter_values in request.filters.items():
            if filter_values and filter_key in aggregations:
                filter_col = aggregations[filter_key]
                escaped = [v.replace("'", "''") for v in filter_values]
                values_str = "', '".join(escaped)
                where_parts.append(f"{filter_col} IN ('{values_str}')")

    if request.not_in_filters:
        for filter_key, filter_values in request.not_in_filters.items():
            if filter_values and filter_key in aggregations:
                filter_col = aggregations[filter_key]
                escaped = [v.replace("'", "''") for v in filter_values]
                values_str = "', '".join(escaped)
                where_parts.append(f"{filter_col} NOT IN ('{values_str}')")

    placeholders[f"{source_name}__where_clause"] = " AND ".join(where_parts) if where_parts else "1=1"

    # {source__group_by}
    group_parts = []
    if request.include_date and transformed_date:
        group_parts.append(transformed_date)
    if request.include_time and transformed_time:
        group_parts.append(transformed_time)
    if agg_col:
        group_parts.append(agg_col)
    placeholders[f"{source_name}__group_by"] = ", ".join(group_parts) if group_parts else "1"

    # {source__order_by}
    order_parts = []
    if request.include_date and transformed_date:
        order_parts.append(transformed_date)
    if request.include_time and transformed_time:
        order_parts.append(transformed_time)
    placeholders[f"{source_name}__order_by"] = ", ".join(order_parts) if order_parts else "1"

    placeholders[f"{source_name}__time_join_condition"] = ""

    return placeholders


def _build_join_on_placeholder(
    join_config: Dict,
    sources: Dict,
    request: QueryRequest,
    transform_config: Dict,
    include_time: bool
) -> Dict[str, str]:
    """Build JOIN ON placeholder for a pair of sources."""

    left_name = join_config.get("left")
    right_name = join_config.get("right")

    if not left_name or not right_name:
        return {}

    left_config = sources.get(left_name, {})
    right_config = sources.get(right_name, {})

    if not left_config or not right_config:
        return {}

    conditions = []

    # Date condition
    if join_config.get("include_date", True):
        left_date = left_config.get("date_col")
        right_date = right_config.get("date_col")
        if left_date and right_date:
            date_transform = transform_config["date_transform"]
            conditions.append(
                f"{date_transform.format(col=left_date)} = {date_transform.format(col=right_date)}"
            )

    # Time condition (only if HOURLY and configured)
    if join_config.get("include_time", True) and include_time:
        left_time = left_config.get("time_col")
        right_time = right_config.get("time_col")
        if left_time and right_time:
            conditions.append(f"{left_time} = {right_time}")

    # Aggregation condition
    if join_config.get("include_aggregation", True) and request.aggregation_level:
        left_agg_col = left_config.get("aggregations", {}).get(request.aggregation_level)
        right_agg_col = right_config.get("aggregations", {}).get(request.aggregation_level)
        if left_agg_col and right_agg_col:
            conditions.append(f"{left_agg_col} = {right_agg_col}")

    # Custom static conditions
    for custom_cond in join_config.get("custom", []):
        conditions.append(custom_cond)

    placeholder_key = f"{left_name}__{right_name}__join_on"
    return {placeholder_key: " AND ".join(conditions) if conditions else "1=1"}


# ============================================================================
# CORE BUILDER
# ============================================================================

def build_raw_sql_query(request: QueryRequest, config: Dict) -> str:
    """Build final SQL from a raw_sql config by replacing all placeholders."""

    sources = config.get("sources", {})
    sql_template = config["sql_template"]
    granularity = request.time_granularity

    time_granularities = config.get("time_granularities", {})
    if granularity not in time_granularities:
        raise ValueError(
            f"Granularity '{granularity}' not available. Options: {list(time_granularities.keys())}"
        )
    if not time_granularities[granularity].get("is_available", True):
        raise ValueError(f"Granularity '{granularity}' is not available for this query")

    transform_config = GRANULARITY_TRANSFORMS.get(granularity, GRANULARITY_TRANSFORMS["DAILY"])
    include_time = transform_config["include_time"]

    # --- Cross-source consistency validation ---
    # If something is needed, it must be defined in ALL sources — no silent skips.

    # date_col: required in all sources when include_date is True
    # (unless source has no_date: True)
    if request.include_date:
        missing_date = [n for n, c in sources.items() if not c.get("no_date") and not c.get("date_col")]
        if missing_date:
            raise ValueError(
                f"'include_date' is True but source(s) {missing_date} have no 'date_col' defined."
            )

    # time_col: required in all sources when granularity is HOURLY
    # (unless source has no_time: True)
    if include_time:
        missing_time = [n for n, c in sources.items() if not c.get("no_time") and not c.get("time_col")]
        if missing_time:
            raise ValueError(
                f"Granularity 'HOURLY' requested but source(s) {missing_time} have no 'time_col' defined."
            )

    # aggregation_level: if requested, must be defined in all sources
    # (unless source has no_aggregation: True)
    if request.aggregation_level:
        missing_agg = [
            n for n, c in sources.items()
            if not c.get("no_aggregation") and request.aggregation_level not in c.get("aggregations", {})
        ]
        if missing_agg:
            raise ValueError(
                f"Aggregation level '{request.aggregation_level}' requested but "
                f"source(s) {missing_agg} don't have it defined in 'aggregations'."
            )

    placeholders = {}

    for source_name, source_config in sources.items():
        placeholders.update(
            _build_source_placeholders(source_name, source_config, request, transform_config, include_time)
        )

    for join_config in config.get("joins", []):
        placeholders.update(
            _build_join_on_placeholder(join_config, sources, request, transform_config, include_time)
        )

    try:
        return sql_template.format(**placeholders).strip()
    except KeyError as e:
        raise ValueError(f"Missing placeholder in SQL template: {e}")


# ============================================================================
# PUBLIC ENTRY POINT
# ============================================================================

def generate_raw_sql(
    query_category: str,
    query_name: str,
    time_granularity: str = "DAILY",
    query_subcategory: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    multiple_date: Optional[List[str]] = None,
    start_hour: Optional[int] = None,
    end_hour: Optional[int] = None,
    multiple_hour: Optional[List[int]] = None,
    aggregation_level: Optional[str] = None,
    include_date: bool = True,
    include_time: bool = False,
    selected_kpis: Optional[List[str]] = None,
    filters: Optional[Dict[str, List[str]]] = None,
    not_in_filters: Optional[Dict[str, List[str]]] = None,
) -> str:
    """
    Main entry point. Looks up config, builds and returns the final SQL string.

    Example:
        sql = generate_raw_sql(
            query_category="3G",
            query_subcategory="COMBINED",
            query_name="NETWORK",
            time_granularity="DAILY",
            start_date="2025-01-01",
            end_date="2025-01-31",
        )
    """
    config = get_query_config(query_category, query_subcategory, query_name)

    if config.get("query_type") != "raw_sql":
        raise ValueError(
            f"Query '{query_name}' is type '{config.get('query_type')}', not 'raw_sql'"
        )

    request = QueryRequest(
        query_category=query_category,
        query_subcategory=query_subcategory,
        query_name=query_name,
        time_granularity=time_granularity,
        start_date=start_date,
        end_date=end_date,
        multiple_date=multiple_date,
        start_hour=start_hour,
        end_hour=end_hour,
        multiple_hour=multiple_hour,
        aggregation_level=aggregation_level,
        include_date=include_date,
        include_time=include_time,
        selected_kpis=selected_kpis,
        filters=filters,
        not_in_filters=not_in_filters,
    )

    return build_raw_sql_query(request, config)


# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":




        # --- Test 1: 3G Combined Network (DAILY, no aggregation) ---
    print("=" * 70)
    print("TEST 1 — 2G COMBINED NETWORK | DAILY | no aggregation")
    print("=" * 70)

    # sql = generate_raw_sql(
    #     query_category="2G",
    #     query_subcategory="COMBINED",
    #     query_name="NETWORK",
    #     time_granularity="HOURLY",
    #     include_time = True,
    #     start_date="2025-01-01",
    #     end_date="2025-01-31",
    # )

    sql = generate_raw_sql(
        query_category="4G",
        query_subcategory="ERICSSON",
        query_name="MAIN_KPIS",
        time_granularity="HOURLY",
        aggregation_level='COMMUNE',
        include_time = True,
        start_date="2025-01-01",
        end_date="2025-01-31",
    )

    print(sql)


    # # --- Test 1: 3G Combined Network (DAILY, no aggregation) ---
    # print("=" * 70)
    # print("TEST 1 — 3G COMBINED NETWORK | DAILY | no aggregation")
    # print("=" * 70)
    # sql = generate_raw_sql(
    #     query_category="3G",
    #     query_subcategory="COMBINED",
    #     query_name="NETWORK",
    #     time_granularity="DAILY",
    #     start_date="2025-01-01",
    #     end_date="2025-01-31",
    # )
    # print(sql)

    # # --- Test 2: 3G Combined Network (MONTHLY, no aggregation) ---
    # print("\n" + "=" * 70)
    # print("TEST 2 — 3G COMBINED NETWORK | MONTHLY | no aggregation")
    # print("=" * 70)
    # sql = generate_raw_sql(
    #     query_category="3G",
    #     query_subcategory="COMBINED",
    #     query_name="NETWORK",
    #     time_granularity="MONTHLY",
    #     start_date="2025-01-01",
    #     end_date="2025-12-31",
    # )
    # print(sql)

    # # --- Test 3: TEST_RAW_SQL (DAILY, cell_name aggregation) ---
    # print("\n" + "=" * 70)
    # print("TEST 3 — TEST_RAW_SQL | DAILY | cell_name aggregation")
    # print("=" * 70)
    # sql = generate_raw_sql(
    #     query_category="TEST_RAW_SQL",
    #     query_subcategory="SAMPLE",
    #     query_name="KPI_TEST",
    #     time_granularity="DAILY",
    #     start_date="2025-01-01",
    #     end_date="2025-01-31",
    #     aggregation_level="cell_name",
    # )
    # print(sql)