import pandas as pd
# import mysql.connector
from datetime import datetime

# Step 1: Read the Excel file
def read_excel(file_path):
    df = pd.read_csv(file_path)
    return df

# Step 2: Extract additional fields from BSC6910UCell
def extract_fields(df):
    # Extract CELL_NAME: first element after '='
    df['CELL_NAME'] = df['BSC6910UCell'].str.split(',').str[0].str.split('=').str[-1]
    
    # Extract controller_name: everything before first '/'
    df['controller_name'] = df['NE Name'].str.split('/').str[0]
    
    # Extract Cell_Index: second-to-last element after '='
    df['Cell_Index'] = df['BSC6910UCell'].str.split('=').str[-2].str.split(',').str[0]
    
    # Extract LogicRNCID: last element after '='
    df['LogicRNCID'] = df['BSC6910UCell'].str.split('=').str[-1]
    
    # Extract date and time from Start Time
    df['date'] = pd.to_datetime(df['Start Time']).dt.date
    df['time'] = pd.to_datetime(df['Start Time']).dt.time
    
    # Rename BSC6910UCell to GCELL
    df['GCELL'] = df['BSC6910UCell']

    df

    import numpy as np
    df = df.replace("NIL", None)

    
    return df

# Step 3: Column mapping from report to DB
def create_column_mapping():
    mapping = {
        # Extracted fields
        'date': 'date',
        'time': 'time',
        'GCELL': 'GCELL',
        'CELL_NAME': 'CELL_NAME',
        'controller_name': 'controller_name',
        'Cell_Index': 'Cell_Index',
        'LogicRNCID': 'LogicRNCID',
        
        # RRC counters - replace dots and parentheses
        'RRC.AttConnEstab.OrgStrCall (None)': 'RRC_AttConnEstab_OrgStrCall',
        'RRC.AttConnEstab.OrgInterCall (None)': 'RRC_AttConnEstab_OrgInterCall',
        'RRC.AttConnEstab.OrgBkgCall (None)': 'RRC_AttConnEstab_OrgBkgCall',
        'RRC.AttConnEstab.OrgSubCall (None)': 'RRC_AttConnEstab_OrgSubCall',
        'RRC.AttConnEstab.TmStrCall (None)': 'RRC_AttConnEstab_TmStrCall',
        'RRC.AttConnEstab.TmInterCall (None)': 'RRC_AttConnEstab_TmInterCall',
        'RRC.AttConnEstab.TmBkgCall (None)': 'RRC_AttConnEstab_TmBkgCall',
        'RRC.SuccConnEstab.OrgStrCall (None)': 'RRC_SuccConnEstab_OrgStrCall',
        'RRC.SuccConnEstab.OrgInterCall (None)': 'RRC_SuccConnEstab_OrgInterCall',
        'RRC.SuccConnEstab.OrgBkgCall (None)': 'RRC_SuccConnEstab_OrgBkgCall',
        'RRC.SuccConnEstab.OrgSubCall (None)': 'RRC_SuccConnEstab_OrgSubCall',
        'RRC.SuccConnEstab.TmStrCall (None)': 'RRC_SuccConnEstab_TmStrCall',
        'RRC.SuccConnEstab.TmItrCall (None)': 'RRC_SuccConnEstab_TmItrCall',
        'RRC.SuccConnEstab.TmBkgCall (None)': 'RRC_SuccConnEstab_TmBkgCall',
        'VS.RAB.AttEstabPS.Conv (None)': 'VS_RAB_AttEstabPS_Conv',
        'VS.RAB.AttEstabPS.Str (None)': 'VS_RAB_AttEstabPS_Str',
        'VS.RAB.AttEstabPS.Int (None)': 'VS_RAB_AttEstabPS_Int',
        'VS.RAB.AttEstabPS.Bkg (None)': 'VS_RAB_AttEstabPS_Bkg',
        'VS.RAB.SuccEstabPS.Conv (None)': 'VS_RAB_SuccEstabPS_Conv',
        'VS.RAB.SuccEstabPS.Str (None)': 'VS_RAB_SuccEstabPS_Str',
        'VS.RAB.SuccEstabPS.Int (None)': 'VS_RAB_SuccEstabPS_Int',
        'VS.RAB.SuccEstabPS.Bkg (None)': 'VS_RAB_SuccEstabPS_Bkg',
        'VS.SHO.AttRLAdd (None)': 'VS_SHO_AttRLAdd',
        'VS.SHO.SuccRLAdd (None)': 'VS_SHO_SuccRLAdd',
        'VS.SHO.AttRLDel (None)': 'VS_SHO_AttRLDel',
        'VS.SHO.SuccRLDel (None)': 'VS_SHO_SuccRLDel',
        'IRATHO.AttOutCS (None)': 'IRATHO_AttOutCS',
        'IRATHO.SuccOutCS (None)': 'IRATHO_SuccOutCS',
        'VS.AMR.Erlang.BestCell (None)': 'VS_AMR_Erlang_BestCell',
        'VS.RRC.AttConnEstab.EDCH (None)': 'VS_RRC_AttConnEstab_EDCH',
        'VS.RRC.AttConnEstab.HSDSCH (None)': 'VS_RRC_AttConnEstab_HSDSCH',
        'VS.RRC.SuccConnEstab.EDCH (None)': 'VS_RRC_SuccConnEstab_EDCH',
        'VS.RRC.SuccConnEstab.HSDSCH (None)': 'VS_RRC_SuccConnEstab_HSDSCH',
        'VS.HSDPA.MeanChThroughput (kbit/s)': 'VS_HSDPA_MeanChThroughput',
        'VS.HSUPA.MeanChThroughput (kbit/s)': 'VS_HSUPA_MeanChThroughput',
    }
    return mapping

# Step 4: Rename columns to match DB
def rename_columns(df, mapping):
    # Only keep columns that exist in mapping
    existing_cols = [col for col in mapping.keys() if col in df.columns]
    df_mapped = df[existing_cols].copy()
    df_mapped.rename(columns=mapping, inplace=True)
    return df_mapped

# Step 5: Insert data into database
def insert_to_db(df, db_config, table_name, batch_size=1, sleep_interval=1):
    import time
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Get column names
    cols = ','.join(df.columns)
    placeholders = ','.join(['%s'] * len(df.columns))
    
    insert_query = f"REPLACE INTO {table_name} ({cols}) VALUES ({placeholders})"
    
    # Replace NaN with None for SQL NULL
    df = df.where(pd.notna(df), None)
    
    # Convert dataframe to list of tuples
    data = [tuple(row) for row in df.values]
    
    total_rows = len(data)
    print(f"Total rows to insert: {total_rows}")
    
    # Insert one by one with batch commit and sleep
    for i, row in enumerate(data, 1):
        cursor.execute(insert_query, row)
        
        # Commit every batch_size rows
        if i % batch_size == 0:
            conn.commit()
            print(f"Progress: {i}/{total_rows} rows inserted ({(i/total_rows)*100:.1f}%)")
            #quit()
            #time.sleep(sleep_interval)
    
    # Final commit for remaining rows
    print("Finalizing insertion...")
    conn.commit()
    print(f"Completed! Total {total_rows} rows inserted into {table_name}")
    
    cursor.close()
    conn.close()

# Step 5: Generate SQL file instead of direct insert
def generate_sql_file(df, table_name, output_file='excel_output/insert_data_3g_counters2.sql', batch_size=5000):
    
    # Replace NaN with None for SQL NULL
    df = df.where(pd.notna(df), None)
    
    # Get column names
    cols = '`' + '`, `'.join(df.columns) + '`'
    
    total_rows = len(df)
    print(f"Total rows to process: {total_rows}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            
            # Start REPLACE statement
            f.write(f"REPLACE INTO `{table_name}` ({cols}) VALUES\n")
            
            # Write each row
            for idx, row in enumerate(batch_df.values):
                # Format values - escape quotes and handle None
                values = []
                for val in row:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, str):
                        # Escape single quotes
                        escaped = val.replace("'", "\\'")
                        values.append(f"'{escaped}'")
                    else:
                        values.append(f"'{val}'")
                
                row_str = '(' + ', '.join(values) + ')'
                
                # Add comma if not last row in batch
                if idx < len(batch_df) - 1:
                    f.write(f"    {row_str},\n")
                else:
                    f.write(f"    {row_str};\n\n")
            
            print(f"Progress: {min(i+batch_size, total_rows)}/{total_rows} rows written ({(min(i+batch_size, total_rows)/total_rows)*100:.1f}%)")
    
    print(f"SQL file generated: {output_file}")
    print(f"You can execute it with: mysql -u username -p database_name < {output_file}")

# Main execution function
def main(excel_file, db_config, table_name):
    print("Step 1: Reading Excel file...")
    df = read_excel(excel_file)
    print(f"Loaded {len(df)} rows")
    
    print("\nStep 2: Extracting additional fields...")
    df = extract_fields(df)
    
    print("\nStep 3: Creating column mapping...")
    mapping = create_column_mapping()
    
    print("\nStep 4: Renaming columns to match DB...")
    df_final = rename_columns(df, mapping)
    print(f"Final columns: {list(df_final.columns)}")
    
    #print("\nStep 5: Inserting data into database...")
    #insert_to_db(df_final, db_config, table_name)

    print("\nStep 6: Generating SQL file...")
    generate_sql_file(df_final, table_name)
    
    print("\nDone!")
    return df_final

# Example usage
if __name__ == "__main__":
    # Configure your database connection
    db_config = {
        'host': '10.22.33.117',
        'user': 'root',
        'password': 'performance',
        'database': 'performanceroute'
    }
    
    # Specify your Excel file path and table name
    excel_file = r'C:\Users\o84432318\Downloads\HOURLY_3G_ALL_COUNTERS_222(2026-01-06 185224)_20260106_195815.csv'  # Change this to your file path
    table_name = 'hourly_huawei_3g_all_counters_2'   # Change this to your table name
    
    # Run the import
    df_result = main(excel_file, db_config, table_name)
    
    # Optional: Preview the data
    print("\nPreview of transformed data:")
    print(df_result.head())