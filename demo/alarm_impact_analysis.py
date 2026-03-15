"""
Alarm Impact Analysis on BSC/RNC Traffic

This script compares traffic during an alarm period against a 4-week historical baseline
to identify the impact on BSC/RNC traffic.

Usage:
    python alarm_impact_analysis.py
"""

import pandas as pd
import mysql.connector
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': '10.22.33.116',
    'user': 'root',
    'password': 'performance',
    'database': 'performanceroute'
}


def get_controller_traffic(alarm_date, start_hour, controllers=None):
    """
    Retrieve controller traffic for alarm day and 4 previous weeks.

    Args:
        alarm_date: Alarm date (format: 'YYYY-MM-DD')
        start_hour: Start hour (0-23)
        controllers: List of BSC/RNC names to analyze (e.g., ['BHBSC03', 'HQRNC01'])
                    If None, analyzes all controllers

    Returns:
        pandas.DataFrame: Combined data with alarm day and historical weeks
    """

    # Calculate date ranges
    alarm_dt = datetime.strptime(alarm_date, '%Y-%m-%d')
    week1_dt = alarm_dt - timedelta(days=7)
    week2_dt = alarm_dt - timedelta(days=14)
    week3_dt = alarm_dt - timedelta(days=21)
    week4_dt = alarm_dt - timedelta(days=28)

    dates = [
        alarm_dt.strftime('%Y-%m-%d'),
        week1_dt.strftime('%Y-%m-%d'),
        week2_dt.strftime('%Y-%m-%d'),
        week3_dt.strftime('%Y-%m-%d'),
        week4_dt.strftime('%Y-%m-%d')
    ]

    print(f"Analyzing traffic for:")
    print(f"  Alarm date: {dates[0]}")
    print(f"  Week -1:    {dates[1]}")
    print(f"  Week -2:    {dates[2]}")
    print(f"  Week -3:    {dates[3]}")
    print(f"  Week -4:    {dates[4]}")
    print(f"  Hours:      {start_hour}:00 to 23:00")
    if controllers:
        print(f"  Controllers: {', '.join(controllers)}")
    else:
        print(f"  Controllers: ALL")

    # Build controller filter
    if controllers:
        controller_list_str = "', '".join(controllers)
        controller_filter = f"AND controler IN ('{controller_list_str}')"
    else:
        controller_filter = ""

    # Build date list for SQL IN clause
    dates_str = "', '".join(dates)

    query = f"""
    WITH controller_raw AS (
        SELECT
            DATE,
            HOUR(STR_TO_DATE(heur, '%H:%i:%s')) AS heur,
            bsc AS controler,
            ROUND(SUM(CAST(valeur AS DECIMAL(10,2))), 2) AS total_voice_controller,
            'BSC' AS node_type
        FROM ericsson2g_voix
        WHERE date IN ('{dates_str}')
          AND HOUR(STR_TO_DATE(heur, '%H:%i:%s')) BETWEEN {start_hour} AND 23
        GROUP BY DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')), bsc

        UNION ALL

        SELECT
            DATE,
            HOUR(STR_TO_DATE(heur, '%H:%i:%s')),
            rnc AS controler,
            ROUND(SUM(CAST(valeur AS DECIMAL(10,2))), 2),
            'RNC' AS node_type
        FROM ericsson3g_voix
        WHERE date IN ('{dates_str}')
          AND HOUR(STR_TO_DATE(heur, '%H:%i:%s')) BETWEEN {start_hour} AND 23
        GROUP BY DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')), rnc

        UNION ALL

        SELECT
            date,
            HOUR(STR_TO_DATE(time, '%H:%i:%s')),
            controller AS controler,
            ROUND(SUM(Total_Voice), 2),
            'BSC' AS node_type
        FROM hourly_huawei_trafic_per_cell_site_2g
        WHERE date IN ('{dates_str}')
          AND HOUR(STR_TO_DATE(time, '%H:%i:%s')) BETWEEN {start_hour} AND 23
        GROUP BY date, HOUR(STR_TO_DATE(time, '%H:%i:%s')), controller

        UNION ALL

        SELECT
            date,
            HOUR(STR_TO_DATE(time, '%H:%i:%s')),
            controller AS controler,
            ROUND(SUM(Total_Voice), 2),
            'RNC' AS node_type
        FROM hourly_huawei_trafic_per_cell_site_3g
        WHERE date IN ('{dates_str}')
          AND HOUR(STR_TO_DATE(time, '%H:%i:%s')) BETWEEN {start_hour} AND 23
        GROUP BY date, HOUR(STR_TO_DATE(time, '%H:%i:%s')), controller
    )
    SELECT
        DATE,
        heur,
        controler,
        node_type,
        SUM(total_voice_controller) AS traffic
    FROM controller_raw
    WHERE 1=1
      {controller_filter}
    GROUP BY DATE, heur, controler, node_type
    ORDER BY controler, DATE, heur
    """

    # Execute query
    conn = mysql.connector.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()

    # Ensure DATE column is string type for consistent comparison
    if not df.empty:
        df['DATE'] = df['DATE'].astype(str)

    return df, dates


def analyze_impact(df, alarm_date, dates):
    """
    Calculate 4-week average and compare with alarm day.

    Args:
        df: DataFrame with traffic data
        alarm_date: Alarm date string
        dates: List of dates [alarm_date, week1_date, week2_date, week3_date, week4_date]

    Returns:
        pandas.DataFrame: Analysis results with comparison
    """

    # Separate alarm day from historical weeks
    alarm_data = df[df['DATE'] == alarm_date].copy()
    historical_data = df[df['DATE'] != alarm_date].copy()

    # Calculate 4-week average
    avg_data = historical_data.groupby(['heur', 'controler', 'node_type'])['traffic'].mean().reset_index()
    avg_data.rename(columns={'traffic': 'avg_traffic_4weeks'}, inplace=True)

    # Pivot historical data to get individual week columns
    week1_data = df[df['DATE'] == dates[1]][['heur', 'controler', 'node_type', 'traffic']].copy()
    week1_data.rename(columns={'traffic': f'JJ-7 ({dates[1]})'}, inplace=True)

    week2_data = df[df['DATE'] == dates[2]][['heur', 'controler', 'node_type', 'traffic']].copy()
    week2_data.rename(columns={'traffic': f'JJ-14 ({dates[2]})'}, inplace=True)

    week3_data = df[df['DATE'] == dates[3]][['heur', 'controler', 'node_type', 'traffic']].copy()
    week3_data.rename(columns={'traffic': f'JJ-21 ({dates[3]})'}, inplace=True)

    week4_data = df[df['DATE'] == dates[4]][['heur', 'controler', 'node_type', 'traffic']].copy()
    week4_data.rename(columns={'traffic': f'JJ-28 ({dates[4]})'}, inplace=True)

    # Merge alarm data with average
    comparison = alarm_data.merge(
        avg_data,
        on=['heur', 'controler', 'node_type'],
        how='left'
    )

    # Merge individual week data
    comparison = comparison.merge(
        week1_data,
        on=['heur', 'controler', 'node_type'],
        how='left'
    )

    comparison = comparison.merge(
        week2_data,
        on=['heur', 'controler', 'node_type'],
        how='left'
    )

    comparison = comparison.merge(
        week3_data,
        on=['heur', 'controler', 'node_type'],
        how='left'
    )

    comparison = comparison.merge(
        week4_data,
        on=['heur', 'controler', 'node_type'],
        how='left'
    )

    # Calculate difference and percentage change
    comparison['difference'] = comparison['traffic'] - comparison['avg_traffic_4weeks']
    comparison['pct_change'] = ((comparison['traffic'] - comparison['avg_traffic_4weeks']) /
                                 comparison['avg_traffic_4weeks'] * 100)

    # Round for readability
    comparison['avg_traffic_4weeks'] = comparison['avg_traffic_4weeks'].round(2)
    comparison[f'JJ-7 ({dates[1]})'] = comparison[f'JJ-7 ({dates[1]})'].round(2)
    comparison[f'JJ-14 ({dates[2]})'] = comparison[f'JJ-14 ({dates[2]})'].round(2)
    comparison[f'JJ-21 ({dates[3]})'] = comparison[f'JJ-21 ({dates[3]})'].round(2)
    comparison[f'JJ-28 ({dates[4]})'] = comparison[f'JJ-28 ({dates[4]})'].round(2)
    comparison['difference'] = comparison['difference'].round(2)
    comparison['pct_change'] = comparison['pct_change'].round(2)

    # Rename columns for clarity
    comparison.rename(columns={
        'DATE': 'alarm_date',
        'heur': 'hour',
        'traffic': f'Alarm ({alarm_date})'
    }, inplace=True)

    # Reorder columns
    comparison = comparison[['alarm_date', 'hour', 'controler', 'node_type',
                            f'Alarm ({alarm_date})', 'avg_traffic_4weeks',
                            f'JJ-7 ({dates[1]})', f'JJ-14 ({dates[2]})', f'JJ-21 ({dates[3]})', f'JJ-28 ({dates[4]})',
                            'difference', 'pct_change']]

    # Sort by controller and hour
    comparison = comparison.sort_values(['controler', 'hour']).reset_index(drop=True)

    return comparison


def get_summary_stats(comparison_df):
    """
    Generate summary statistics for each controller.

    Args:
        comparison_df: DataFrame with comparison results

    Returns:
        pandas.DataFrame: Summary statistics
    """

    summary = comparison_df.groupby(['controler', 'node_type']).agg({
        'alarm_traffic': 'sum',
        'avg_traffic_4weeks': 'sum',
        'difference': 'sum',
        'pct_change': 'mean'
    }).reset_index()

    summary.rename(columns={
        'alarm_traffic': 'total_alarm_traffic',
        'avg_traffic_4weeks': 'total_avg_traffic',
        'difference': 'total_difference',
        'pct_change': 'avg_pct_change'
    }, inplace=True)

    # Round values
    summary['total_alarm_traffic'] = summary['total_alarm_traffic'].round(2)
    summary['total_avg_traffic'] = summary['total_avg_traffic'].round(2)
    summary['total_difference'] = summary['total_difference'].round(2)
    summary['avg_pct_change'] = summary['avg_pct_change'].round(2)

    # Sort by total difference (most impacted first)
    summary = summary.sort_values('total_difference').reset_index(drop=True)

    return summary


def main(alarm_date, start_hour, controllers=None):
    """
    Main execution function.

    Args:
        alarm_date: Alarm date (format: 'YYYY-MM-DD')
        start_hour: Start hour (0-23)
        controllers: List of BSC/RNC names (optional)

    Returns:
        tuple: (detailed_comparison_df, summary_df)
    """

    print("=" * 80)
    print("ALARM IMPACT ANALYSIS - BSC/RNC Traffic")
    print("=" * 80)

    # Step 1: Retrieve data
    print("\nStep 1: Retrieving traffic data...")
    df, dates = get_controller_traffic(alarm_date, start_hour, controllers)

    if df.empty:
        print("\nNo data found for the specified parameters!")
        return None, None

    print(f"\nRetrieved {len(df)} records")

    # Step 2: Analyze impact
    print("\nStep 2: Analyzing impact...")
    comparison = analyze_impact(df, alarm_date, dates)

    # Step 3: Generate summary
    print("\nStep 3: Generating summary statistics...")
    #summary = get_summary_stats(comparison)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    # Display summary
    print("\nSUMMARY BY CONTROLLER:")
    print("-" * 80)
    #print(summary.to_string(index=False))

    print("\n" + "=" * 80)
    print(f"\nDetailed results available in the returned DataFrames")
    print(f"  - comparison_df: Hourly comparison ({len(comparison)} rows)")
    #print(f"  - summary_df: Controller summary ({len(summary)} rows)")

    # Save to Excel files
    print("\nSaving results to Excel files...")

    import os
    output_dir = 'excel_output'
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with date and controller info
    if controllers:
        controller_str = '_'.join(controllers[:3])  # Limit to first 3 controllers for filename
        if len(controllers) > 3:
            controller_str += f'_plus{len(controllers)-3}'
    else:
        controller_str = 'ALL'

    detailed_file = os.path.join(output_dir, f'alarm_impact_detailed_{alarm_date}_h{start_hour}_{controller_str}.xlsx')
    summary_file = os.path.join(output_dir, f'alarm_impact_summary_{alarm_date}_h{start_hour}_{controller_str}.xlsx')

    comparison.to_excel(detailed_file, index=False, sheet_name='Detailed Comparison')
    #summary.to_excel(summary_file, index=False, sheet_name='Summary')

    print(f"  - Detailed results: {detailed_file}")
    print(f"  - Summary results:  {summary_file}")

    return comparison, 
    #summary


# Example usage
if __name__ == "__main__":
    # Configuration
    alarm_date = "2025-12-19"
    start_hour = 0  # 08:00 (8:00 AM)
    controllers = ['BHBSC04']  # Specify controllers or use None for all

    # Run analysis
    comparison_df, summary_df = main(
        alarm_date=alarm_date,
        start_hour=start_hour,
        controllers=controllers
    )

    # Display sample of detailed results
    if comparison_df is not None:
        print("\n" + "=" * 80)
        print("SAMPLE DETAILED RESULTS (First 10 rows):")
        print("-" * 80)
        print(comparison_df.head(10).to_string(index=False))

        # Optionally save to Excel
        # comparison_df.to_excel('alarm_impact_detailed.xlsx', index=False)
        # summary_df.to_excel('alarm_impact_summary.xlsx', index=False)
        # print("\nResults saved to Excel files!")
