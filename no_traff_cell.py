
# Create a single-sheet Excel report stacking all tables with spacing and a chart.
import pandas as pd
from datetime import datetime
import os
import mysql.connector





# data = [
#     ("2025-09-21", "DBORI1"), ("2025-09-24", "DBORI1"), ("2025-09-20", "DBORI1"),
#     ("2025-09-23", "DBORI1"), ("2025-09-22", "DBORI1"), ("2025-09-20", "DBORI2"),
#     ("2025-09-23", "DBORI2"), ("2025-09-22", "DBORI2"), ("2025-09-21", "DBORI2"),
#     ("2025-09-24", "DBORI2"), ("2025-09-24", "DBORI3"), ("2025-09-20", "DBORI3"),
#     ("2025-09-23", "DBORI3"), ("2025-09-22", "DBORI3"), ("2025-09-21", "DBORI3"),
#     ("2025-09-20", "DNIKKI2"), ("2025-09-23", "DNIKKI2"), ("2025-09-22", "DNIKKI2"),
#     ("2025-09-21", "DNIKKI2"), ("2025-09-24", "DNIKKI2"), ("2025-09-20", "DSERA1"),
#     ("2025-09-23", "DSERA1"), ("2025-09-22", "DSERA1"), ("2025-09-21", "DSERA1"),
#     ("2025-09-24", "DSERA1"), ("2025-09-22", "DSERA2"), ("2025-09-21", "DSERA2"),
#     ("2025-09-24", "DSERA2"), ("2025-09-20", "DSERA2"), ("2025-09-23", "DSERA2"),
#     ("2025-09-23", "GNANS3"), ("2025-09-22", "GNANS3"), ("2025-09-24", "GNANS3"),
#     ("2025-09-21", "GNANS3"), ("2025-09-20", "GNANS3"), ("2025-09-21", "PAR242"),
#     ("2025-09-20", "PAR242"), ("2025-09-21", "BEMB22"), ("2025-09-24", "BEMB22"),
#     ("2025-09-20", "BEMB22"), ("2025-09-23", "BEMB22"), ("2025-09-22", "BEMB22"),
#     ("2025-09-20", "BOUKA3"), ("2025-09-23", "BOUKA3"), ("2025-09-22", "BOUKA3"),
#     ("2025-09-21", "BOUKA3"), ("2025-09-24", "BOUKA3"), ("2025-09-22", "DLIBA3"),
#     ("2025-09-21", "DLIBA3"), ("2025-09-24", "DLIBA3"), ("2025-09-20", "DLIBA3"),
#     ("2025-09-23", "DLIBA3"), ("2025-09-21", "GOROU1"), ("2025-09-20", "GOROU1"),
#     ("2025-09-23", "GOROU1"), ("2025-09-22", "GOROU1"), ("2025-09-24", "GOROU1"),
#     ("2025-09-22", "KAND32"), ("2025-09-24", "KAND32"), ("2025-09-21", "KAND32"),
#     ("2025-09-20", "KAND32"), ("2025-09-23", "KAND32"), ("2025-09-22", "KEROU2"),
#     ("2025-09-24", "KEROU2"), ("2025-09-21", "KEROU2"), ("2025-09-20", "KEROU2"),
#     ("2025-09-23", "KEROU2")
# ]

# # Build dataframe
# df = pd.DataFrame(data, columns=['date', 'CELL_NAME'])
# df['date'] = pd.to_datetime(df['date'] , errors='coerce')

# # report any rows that failed parsing
# bad_dates = df[df['date'].isna()]
# if not bad_dates.empty:
#     print("Warning: some date values could not be parsed:")
#     print(bad_dates)

# # Basic summaries
# outage_days = df.groupby('CELL_NAME').size().reset_index(name='outage_days').sort_values('outage_days', ascending=False)
# all_dates = sorted(df['date'].unique())
# all_cells = sorted(df['CELL_NAME'].unique())

# daily_outages = df.groupby('date').size().reset_index(name='cells_down').sort_values('date')

# # Day-to-day comparison
# date_comparison_rows = []
# for i in range(1, len(all_dates)):
#     current_date = all_dates[i]
#     previous_date = all_dates[i-1]
#     current_cells = set(df[df['date'] == current_date]['CELL_NAME'].tolist())
#     previous_cells = set(df[df['date'] == previous_date]['CELL_NAME'].tolist())
#     newly_failed = current_cells - previous_cells
#     recovered = previous_cells - current_cells
#     still_down = current_cells & previous_cells
#     date_comparison_rows.append({
#         'date': current_date, 'previous_date': previous_date,
#         'newly_failed': len(newly_failed), 'recovered': len(recovered),
#         'still_down': len(still_down), 'total_down': len(current_cells),
#         'newly_failed_list': ','.join(sorted(newly_failed)), 'recovered_list': ','.join(sorted(recovered))
#     })
# date_comparison = pd.DataFrame(date_comparison_rows)

# # Site-level (extract site prefix letters)
# df['site'] = df['CELL_NAME'].str.extract(r'^([A-Z]+)')
# site_analysis = df.groupby('site').agg(unique_cells=('CELL_NAME','nunique'), total_outages=('CELL_NAME','count'), days_affected=('date','nunique')).reset_index().sort_values('total_outages', ascending=False)

# # Prepare export DataFrames
# outage_summary = outage_days.copy()
# outage_summary['outage_percentage'] = (outage_summary['outage_days'] / len(all_dates)) * 100
# outage_summary['priority'] = outage_summary['outage_days'].apply(lambda x: 'CRITICAL' if x == len(all_dates) else ('MEDIUM' if x >= 3 else 'LOW'))

# daily_summary = daily_outages.copy()
# daily_summary['day_name'] = daily_summary['date'].dt.strftime('%A')
# total_cells_monitored = len(all_cells)
# daily_summary['stability_percentage'] = ((total_cells_monitored - daily_summary['cells_down']) / total_cells_monitored) * 100

# # Build single-sheet report
# output_path = "/home/oloko/Documents/huawei_work/draft/no_traff_cell/cell_outage_report_single_sheet.xlsx"
# with pd.ExcelWriter(output_path, engine='xlsxwriter', datetime_format='yyyy-mm-dd', date_format='yyyy-mm-dd') as writer:
#     workbook  = writer.book
#     ws = workbook.add_worksheet('report')
#     writer.sheets['report'] = ws

#     # Formats
#     header_fmt = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#F2F2F2'})
#     bold_fmt = workbook.add_format({'bold': True})
#     date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})
#     small_gap = 1  # rows gap between tables

#     # Helper to write a dataframe at a specific row
#     def write_df_to_ws(df_to_write, start_row, sheet_ws, include_index=False):
#         sheet_ws.write_row(start_row, 0, list(df_to_write.columns), header_fmt)
#         for r_idx, row in enumerate(df_to_write.values, start=1):
#             for c_idx, val in enumerate(row):
#                 if isinstance(val, pd.Timestamp):
#                     sheet_ws.write_datetime(start_row + r_idx, c_idx, val.to_pydatetime(), date_fmt)
#                 else:
#                     sheet_ws.write(start_row + r_idx, c_idx, val)
#         return start_row + 1 + len(df_to_write)  # next free row index
    
#     # NEW: Helper to write a dataframe starting at a specific column (left-to-right layout).
#     def write_df_to_ws_horiz(df_to_write, start_col, sheet_ws, start_row=1):
#         # write header across the top at start_row
#         sheet_ws.write_row(start_row, start_col, list(df_to_write.columns), header_fmt)
#         for r_idx, row in enumerate(df_to_write.values, start=1):
#             for c_idx, val in enumerate(row):
#                 row_idx = start_row + r_idx
#                 col_idx = start_col + c_idx
#                 if isinstance(val, pd.Timestamp):
#                     sheet_ws.write_datetime(row_idx, col_idx, val.to_pydatetime(), date_fmt)
#                 else:
#                     sheet_ws.write(row_idx, col_idx, val)
#         # return next free column index (one past the last column used)
#         return start_col + df_to_write.shape[1]


#     # 1) Raw data
#     current_row = 0
#     current_col = 0

#     ws.write(0, current_col, "Raw data", bold_fmt)
#     #current_row += 1
#     #current_row = write_df_to_ws(df[['date','CELL_NAME']], current_row, ws)
#     current_col = write_df_to_ws_horiz(df[['date','CELL_NAME']], current_col, ws)

#     current_col += small_gap

#     # 3) Daily summary
#     ws.write(0, current_col, "Daily summary (daily outages & stability)", bold_fmt)
#     #current_col += 1
#     daily_start_col = current_col
#     daily_start_row = 2
#     daily_summarage_col = write_df_to_ws_horiz(daily_summary[['date','cells_down','day_name','stability_percentage']], current_col, ws)

#     # gap
#     #current_col += small_gap

#     # Insert chart for daily outages next to the daily summary
#     chart = workbook.add_chart({'type': 'column'})
#     chart.add_series({
#         'name':       'Cells down',     
#         'categories': ['report', daily_start_row , daily_start_col, daily_start_row + len(daily_summary), daily_start_col],
#         'values':     ['report', daily_start_row, daily_start_col+1, daily_start_row + len(daily_summary), daily_start_col+1],
#     })
#     chart.set_title({'name': 'Daily Outages'})
#     chart.set_x_axis({'name': 'Date'})
#     chart.set_y_axis({'name': 'Cells down'})
#     # place chart a few columns to the right of the data
#     chart_row =   len(daily_summary) 
#     ws.insert_chart(25, 7, chart, {'x_scale': 1.2, 'y_scale': 1.0})

#     # 2) Outage summary
#     ws.write(len(daily_summary)+4, current_col, "Outage summary (cells ranked by outage days)", bold_fmt)
#     #current_col += 1
#     current_col = write_df_to_ws_horiz(outage_summary, current_col, ws , start_row=len(daily_summary)+5)


    

#     current_col += small_gap

#     # 5) Day-to-day comparison
#     ws.write(0, current_col, "Day-to-day comparison", bold_fmt)
#     #current_col += 1
#     current_col = write_df_to_ws_horiz(date_comparison, current_col, ws)

#     # Some final formatting: column widths
#     for col_idx in range(0, current_col + 5):
#         ws.set_column(col_idx, col_idx, 18)

# print("Single-sheet Excel report generated at:", output_path)




import pandas as pd
from datetime import datetime
import os
import mysql.connector


class CellOutageReportGenerator:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("Database connection established")
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            
    def disconnect_db(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def fetch_data(self, query, sheet_name):
        """Execute query and return DataFrame"""
        if not self.connection:
            print("No database connection")
            return pd.DataFrame()
            
        try:
            df = pd.read_sql_query(query, self.connection)
            print(f"Fetched {len(df)} records for {sheet_name}")
            return df
        except Exception as e:
            print(f"Error fetching data for {sheet_name}: {e}")
            return pd.DataFrame()
    
    def get_queries(self, start_date, end_date):
        """Define all queries with date parameters"""
        return {
            "Huawei_2G_Voice": f"""
                SELECT date, CELL_NAME
                FROM hourly_huawei_trafic_per_cell_site_2g
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, CELL_NAME
                HAVING SUM(Total_Voice) = 0
                ORDER BY date, CELL_NAME
            """,
            
            "Huawei_3G_Voice": f"""
                SELECT date, CELL_NAME
                FROM hourly_huawei_trafic_per_cell_site_3g
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, CELL_NAME
                HAVING SUM(Total_Voice) = 0
                ORDER BY date, CELL_NAME
            """,
            
            "Huawei_3G_Data": f"""
                SELECT date, CELL_NAME
                FROM hourly_huawei_trafic_per_cell_site_3g
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, CELL_NAME
                HAVING SUM(Total_Data) = 0
                ORDER BY date, CELL_NAME
            """,
            
            "Huawei_4G_Data": f"""
                SELECT date, CELL_NAME
                FROM hourly_huawei_trafic_per_cell_site_4g
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, CELL_NAME
                HAVING SUM(Total_Data) = 0
                ORDER BY date, CELL_NAME
            """,
            
            "Ericsson_2G_Data": f"""
                SELECT date_id as date, CELL_NAME
                FROM hourly_ericsson_trafic_per_site_2g
                WHERE date_id BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY DATE_ID, CELL_NAME
                HAVING SUM(Total_Data_Volume) = 0
                ORDER BY DATE_ID, CELL_NAME
            """,
            
            "Ericsson_2G_Voice": f"""
                SELECT date, cell_name AS CELL_NAME
                FROM hourly_ericsson_trafic_per_site_2g_voix
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, cell_name
                HAVING SUM(trafic2gVoix) = 0
                ORDER BY date, cell_name
            """,
            
            "Ericsson_3G_Data": f"""
                SELECT date_id date, UCELL_ID AS CELL_NAME
                FROM hourly_ericsson_trafic_per_site_3g
                WHERE date_id BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, UCELL_ID
                HAVING SUM(Total_Data_Volume) = 0
                ORDER BY date, UCELL_ID
            """,
            
            "Ericsson_3G_Voice": f"""
                SELECT date, UCELL_ID AS CELL_NAME
                FROM hourly_ericsson_trafic_per_site_3g_voix
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, UCELL_ID
                HAVING SUM(trafic_3g_voix) = 0
                ORDER BY date, UCELL_ID
            """,
            
            "Ericsson_4G_Data": f"""
                SELECT date, EUtranCellId AS CELL_NAME
                FROM ericsson4g_data
                WHERE date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY date, EUtranCellId
                HAVING SUM(valeur) = 0
                ORDER BY date, EUtranCellId
            """
        }
    
    def process_dataframe(self, df):
        """Process dataframe similar to original code"""
        if df.empty:
            return None, None, None, None, None
            
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Basic summaries
        outage_days = df.groupby('CELL_NAME').size().reset_index(name='outage_days').sort_values('outage_days', ascending=False)
        all_dates = sorted(df['date'].unique())
        all_cells = sorted(df['CELL_NAME'].unique())
        
        daily_outages = df.groupby('date').size().reset_index(name='cells_down').sort_values('date')
        
        # Day-to-day comparison
        date_comparison_rows = []
        for i in range(1, len(all_dates)):
            current_date = all_dates[i]
            previous_date = all_dates[i-1]
            current_cells = set(df[df['date'] == current_date]['CELL_NAME'].tolist())
            previous_cells = set(df[df['date'] == previous_date]['CELL_NAME'].tolist())
            newly_failed = current_cells - previous_cells
            recovered = previous_cells - current_cells
            still_down = current_cells & previous_cells
            date_comparison_rows.append({
                'date': current_date, 'previous_date': previous_date,
                'newly_failed': len(newly_failed), 'recovered': len(recovered),
                'still_down': len(still_down), 'total_down': len(current_cells),
                'newly_failed_list': ','.join(sorted(newly_failed)), 
                'recovered_list': ','.join(sorted(recovered))
            })
        
        date_comparison = pd.DataFrame(date_comparison_rows)
        
        # Prepare summaries
        outage_summary = outage_days.copy()
        outage_summary['outage_percentage'] = (outage_summary['outage_days'] / len(all_dates)) * 100 if all_dates else 0
        outage_summary['priority'] = outage_summary['outage_days'].apply(
            lambda x: 'CRITICAL' if x == len(all_dates) else ('MEDIUM' if x >= 3 else 'LOW')
        )
        
        daily_summary = daily_outages.copy()
        daily_summary['day_name'] = daily_summary['date'].dt.strftime('%A')
        total_cells_monitored = len(all_cells)
        daily_summary['stability_percentage'] = (
            (total_cells_monitored - daily_summary['cells_down']) / total_cells_monitored * 100
            if total_cells_monitored > 0 else 0
        )
        
        return df, outage_summary, daily_summary, date_comparison, all_dates
    
    def write_to_excel_sheet(self, df, outage_summary, daily_summary, date_comparison, 
                           all_dates, writer, sheet_name):
        """Write processed data to Excel sheet using original formatting logic"""
        if df is None or df.empty:
            print(f"No data to write for {sheet_name}")
            return
            
        workbook = writer.book
        ws = workbook.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = ws
        
        # Formats
        header_fmt = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#F2F2F2'})
        bold_fmt = workbook.add_format({'bold': True})
        date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        small_gap = 1
        
        def write_df_to_ws_horiz(df_to_write, start_col, sheet_ws, start_row=1):
            sheet_ws.write_row(start_row, start_col, list(df_to_write.columns), header_fmt)
            for r_idx, row in enumerate(df_to_write.values, start=1):
                for c_idx, val in enumerate(row):
                    row_idx = start_row + r_idx
                    col_idx = start_col + c_idx
                    if isinstance(val, pd.Timestamp):
                        sheet_ws.write_datetime(row_idx, col_idx, val.to_pydatetime(), date_fmt)
                    else:
                        sheet_ws.write(row_idx, col_idx, val)
            return start_col + df_to_write.shape[1]
        
        # Layout similar to original
        current_row = 0
        current_col = 0
        
        # Raw data
        ws.write(0, current_col, "Raw data", bold_fmt)
        current_col = write_df_to_ws_horiz(df[['date','CELL_NAME']], current_col, ws)
        current_col += small_gap
        
        # Daily summary
        ws.write(0, current_col, "Daily summary (daily outages & stability)", bold_fmt)
        daily_start_col = current_col
        daily_start_row = 2
        current_col = write_df_to_ws_horiz(
            daily_summary[['date','cells_down','day_name','stability_percentage']], 
            current_col, ws
        )
        
        # Chart
        if len(daily_summary) > 0:
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Cells down',
                'categories': ['report', daily_start_row, daily_start_col, 
                             daily_start_row + len(daily_summary), daily_start_col],
                'values': ['report', daily_start_row, daily_start_col+1, 
                          daily_start_row + len(daily_summary), daily_start_col+1],
            })
            chart.set_title({'name': f'Daily Outages - {sheet_name}'})
            chart.set_x_axis({'name': 'Date'})
            chart.set_y_axis({'name': 'Cells down'})
            ws.insert_chart(25, 7, chart, {'x_scale': 1.2, 'y_scale': 1.0})
        
        # Outage summary
        ws.write(len(daily_summary)+4, current_col, "Outage summary (cells ranked by outage days)", bold_fmt)
        current_col = write_df_to_ws_horiz(outage_summary, current_col, ws, 
                                         start_row=len(daily_summary)+5)
        current_col += small_gap
        
        # Day-to-day comparison
        if len(date_comparison) > 0:
            ws.write(0, current_col, "Day-to-day comparison", bold_fmt)
            current_col = write_df_to_ws_horiz(date_comparison, current_col, ws)
        
        # Set column widths
        for col_idx in range(0, current_col + 5):
            ws.set_column(col_idx, col_idx, 18)
    
    def generate_report(self, start_date, end_date, output_path):
        """Generate complete Excel report with multiple sheets"""
        self.connect_db()
        
        try:
            queries = self.get_queries(start_date, end_date)
            
            with pd.ExcelWriter(output_path, engine='xlsxwriter', 
                              datetime_format='yyyy-mm-dd', date_format='yyyy-mm-dd') as writer:
                
                for sheet_name, query in queries.items():
                    print(f"Processing {sheet_name}...")
                    
                    # Fetch data
                    df = self.fetch_data(query, sheet_name)
                    
                    if not df.empty:
                        # Process data
                        processed_data = self.process_dataframe(df)
                        df, outage_summary, daily_summary, date_comparison, all_dates = processed_data
                        
                        # Write to Excel
                        self.write_to_excel_sheet(df, outage_summary, daily_summary, 
                                                date_comparison, all_dates, writer, sheet_name)
                    else:
                        print(f"No data found for {sheet_name}")
            
            print(f"Excel report generated: {output_path}")
            
        finally:
            self.disconnect_db()


# Usage example
if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host':"10.22.33.116",
        'user':"root",
        'password':"performance",
        'database':"performanceroute"
    }
    
    # Initialize generator
    generator = CellOutageReportGenerator(db_config)
    
    # Generate report
    output_path = "./excel_output/cell_outage_report_multi_sheet.xlsx"
    generator.generate_report('2025-12-01', '2025-12-25', output_path)