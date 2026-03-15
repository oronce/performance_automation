import pandas as pd
from datetime import datetime

# Step 1: Read the CSV file
def read_excel(file_path):
   # df = pd.read_csv(file_path)
    df = pd.read_excel(file_path)
    return df

# Step 2: Extract additional fields from GCELL
def extract_fields(df):
    # GCELL format: "LABEL=GODJE3, CellIndex=488, CGI=61602001D43A1"
    # Extract CELL_NAME from GCELL (after LABEL=)
    df['CELL_NAME'] = df['GCELL'].str.split(',').str[0].str.split('=').str[1].str.strip()

    # Extract controller_name from NE Name (no '/' in the data, so use as is)
    df['controller_name'] = df['NE Name'].str.strip()

    # Extract cell_index from GCELL (after CellIndex=)
    df['cell_index'] = df['GCELL'].str.split(',').str[1].str.split('=').str[1].str.strip()

    # Extract CGI from GCELL (after CGI=)
    df['CGI'] = df['GCELL'].str.split(',').str[2].str.split('=').str[1].str.strip()

    # Extract date and time from Start Time
    df['date'] = pd.to_datetime(df['Start Time']).dt.date
    df['time'] = pd.to_datetime(df['Start Time']).dt.time

    # Replace NIL with None
    import numpy as np
    df = df.replace("NIL", None)

    return df

# Step 3: Column mapping from CSV to DB
def create_column_mapping():
    mapping = {
        # Extracted fields
        'date': 'date',
        'time': 'time',
        'GCELL': 'GCELL',
        'CELL_NAME': 'CELL_NAME',
        'controller_name': 'controller_name',
        'cell_index': 'cell_index',
        'CGI': 'CGI',

        # Direct mappings with dots replaced by underscores
        'CELL.SERV.OOS (s)': 'CELL_SERV_OOS',
        'CELL.TRAF.CH.CALL.DROPS (None)': 'CELL_TRAF_CH_CALL_DROPS',
        'CELL.TRAF.CH.CALL.DROPS.IN.STABLE.STATE (None)': 'CELL_TRAF_CH_CALL_DROPS_IN_STABLE_STATE',
        'CELL.TRAF.CH.CALL.DROPS.HO.FAIL (None)': 'CELL_TRAF_CH_CALL_DROPS_HO_FAIL',
        'CELL.TRAF.CH.CALL.DROPS.ABIS.LNK.FAIL (None)': 'CELL_TRAF_CH_CALL_DROPS_ABIS_LNK_FAIL',
        'CELL.TRAF.CH.CALL.DROPS.EQUIP.FAIL (None)': 'CELL_TRAF_CH_CALL_DROPS_EQUIP_FAIL',
        'CELL.TRAF.CH.CALL.DROPS.FORCE.HO (None)': 'CELL_TRAF_CH_CALL_DROPS_FORCE_HO',
        'CELL.SD.CALL.DROPS (None)': 'CELL_SD_CALL_DROPS',
        'CELL.IMM.ASS.SUCC.SD (None)': 'CELL_IMM_ASS_SUCC_SD',
        'CELL.INTRABSC.OUTCELL.HO.SUCC (None)': 'CELL_INTRABSC_OUTCELL_HO_SUCC',
        'CELL.INTRABSC.OUTCELL.HO.CMD (None)': 'CELL_INTRABSC_OUTCELL_HO_CMD',
        'CELL.INTERBSC.OUTCELL.HO.CMD (None)': 'CELL_INTERBSC_OUTCELL_HO_CMD',
        'CELL.INTERBSC.OUTCELL.HO.SUCC (None)': 'CELL_INTERBSC_OUTCELL_HO_SUCC',
        'CELL.KPI.SD.REQ (None)': 'CELL_KPI_SD_REQ',
        'CELL.KPI.SD.CONGEST (None)': 'CELL_KPI_SD_CONGEST',
        'CELL.KPI.SD.SUCC (None)': 'CELL_KPI_SD_SUCC',
        'CELL.KPI.SD.TRAF.ERL (Erl)': 'CELL_KPI_SD_TRAF_ERL',
        'CELL.KPI.TCH.REQ.SIG (None)': 'CELL_KPI_TCH_REQ_SIG',
        'CELL.KPI.TCH.CONG.SIG (None)': 'CELL_KPI_TCH_CONG_SIG',
        'CELL.KPI.TCH.SUCC.SIG (None)': 'CELL_KPI_TCH_SUCC_SIG',
        'CELL.KPI.TCH.DROPS.SIG (None)': 'CELL_KPI_TCH_DROPS_SIG',
        'CELL.KPI.TCH.ASS.REQ.TRAF (None)': 'CELL_KPI_TCH_ASS_REQ_TRAF',
        'CELL.KPI.TCH.ASS.CONG.TRAF (None)': 'CELL_KPI_TCH_ASS_CONG_TRAF',
        'CELL.KPI.TCH.ASS.SUCC.TRAF (None)': 'CELL_KPI_TCH_ASS_SUCC_TRAF',
        'CELL.KPI.TCH.STATIC.DROPS.TRAF (None)': 'CELL_KPI_TCH_STATIC_DROPS_TRAF',
        'CELL.KPI.TCH.HO.REQ.TRAF (None)': 'CELL_KPI_TCH_HO_REQ_TRAF',
        'CELL.KPI.TCH.HO.CONGEST.TRAF (None)': 'CELL_KPI_TCH_HO_CONGEST_TRAF',
        'CELL.KPI.TCH.HO.SUCC.TRAF (None)': 'CELL_KPI_TCH_HO_SUCC_TRAF',
        'CELL.KPI.TCH.HO.DROPS.TRAF (None)': 'CELL_KPI_TCH_HO_DROPS_TRAF',
        'CELL.KPI.TCH.TRAF.ERL.TRAF (Erl)': 'CELL_KPI_TCH_TRAF_ERL_TRAF',
        'CELL.KPI.TCH.AVAIL.NUM (None)': 'CELL_KPI_TCH_AVAIL_NUM',
        'CELL.KPI.TCH.CFG.NUM (None)': 'CELL_KPI_TCH_CFG_NUM',
        'CELL.KPI.TCHH.TRAF.ERL (Erl)': 'CELL_KPI_TCHH_TRAF_ERL',
        'CELL.KPI.TCH.CONGESTION.RATE (%)': 'CELL_KPI_TCH_CONGESTION_RATE',
        'CELL.SD.CALL.DROPS.CALL (None)': 'CELL_SD_CALL_DROPS_CALL',
        'CELL.SD.UM.CALL.DROPS.CALL (None)': 'CELL_SD_UM_CALL_DROPS_CALL',
        'CELL.SD.CALL.DROPS.TA (None)': 'CELL_SD_CALL_DROPS_TA',
        'CELL.SD.CALL.DROPS.RCV.LEVEL (None)': 'CELL_SD_CALL_DROPS_RCV_LEVEL',
        'CELL.SD.CALL.DROPS.QUAL (None)': 'CELL_SD_CALL_DROPS_QUAL',
        'CELL.SD.CALL.DROPS.OTHER (None)': 'CELL_SD_CALL_DROPS_OTHER',
        'CELL.RATE.SD.CONG (%)': 'CELL_RATE_SD_CONG',
        'CELL.TCH.CALL.DROPS.TA (None)': 'CELL_TCH_CALL_DROPS_TA',
        'CELL.TCH.CALL.DROPS.UL.RCV.LEVEL (None)': 'CELL_TCH_CALL_DROPS_UL_RCV_LEVEL',
        'CELL.TCH.CALL.DROPS.DL.RCV.LEVEL (None)': 'CELL_TCH_CALL_DROPS_DL_RCV_LEVEL',
        'CELL.TCH.CALL.DROPS.ULDL.RCV.LEVEL (None)': 'CELL_TCH_CALL_DROPS_ULDL_RCV_LEVEL',
        'CELL.TCH.CALL.DROPS.UL.FER (None)': 'CELL_TCH_CALL_DROPS_UL_FER',
        'CELL.TCH.CALL.DROPS.DL.FER (None)': 'CELL_TCH_CALL_DROPS_DL_FER',
        'CELL.TCH.CALL.DROPS.ULDL.FER (None)': 'CELL_TCH_CALL_DROPS_ULDL_FER',
        'CELL.TCH.CALL.DROPS.UL.QUAL (None)': 'CELL_TCH_CALL_DROPS_UL_QUAL',
        'CELL.TCH.CALL.DROPS.DL.QUAL (None)': 'CELL_TCH_CALL_DROPS_DL_QUAL',
        'CELL.TCH.CALL.DROPS.ULDL.QUAL (None)': 'CELL_TCH_CALL_DROPS_ULDL_QUAL',
        'CELL.TCH.CALL.DROPS.OTHER (None)': 'CELL_TCH_CALL_DROPS_OTHER',
        'CELL.SERV.OOS.OM (s)': 'CELL_SERV_OOS_OM',
        'CELL.SD.CALL.DROPS.LOC.UPDATE (None)': 'CELL_SD_CALL_DROPS_LOC_UPDATE',
    }
    return mapping

# Step 4: Rename columns to match DB
def rename_columns(df, mapping):
    # Only keep columns that exist in mapping
    existing_cols = [col for col in mapping.keys() if col in df.columns]
    df_mapped = df[existing_cols].copy()
    df_mapped.rename(columns=mapping, inplace=True)
    return df_mapped

# Step 5: Generate SQL files with row limit per file
def generate_sql_file(df, table_name, output_file='excel_output/insert_data_2g_huawei.sql', batch_size=5000, max_rows_per_file=500000):

    # Replace NaN with None for SQL NULL
    df = df.where(pd.notna(df), None)

    # Get column names
    cols = '`' + '`, `'.join(df.columns) + '`'

    total_rows = len(df)
    print(f"Total rows to process: {total_rows}")

    # Calculate number of files needed
    num_files = (total_rows + max_rows_per_file - 1) // max_rows_per_file
    print(f"Will create {num_files} file(s)")

    file_counter = 1

    for file_start in range(0, total_rows, max_rows_per_file):
        file_end = min(file_start + max_rows_per_file, total_rows)
        df_file = df.iloc[file_start:file_end]

        # Generate filename with counter
        if num_files > 1:
            base_name = output_file.rsplit('.', 1)[0]
            extension = output_file.rsplit('.', 1)[1] if '.' in output_file else 'sql'
            current_file = f"{base_name}_part{file_counter}.{extension}"
        else:
            current_file = output_file

        print(f"\nGenerating file {file_counter}/{num_files}: {current_file}")

        with open(current_file, 'w', encoding='utf-8') as f:
            for i in range(0, len(df_file), batch_size):
                batch_df = df_file.iloc[i:i+batch_size]

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

                print(f"  Progress: {min(i+batch_size, len(df_file))}/{len(df_file)} rows written")

        print(f"File {file_counter} completed: {file_end - file_start} rows")
        file_counter += 1

    print(f"\nAll files generated successfully!")

# Main execution function
def main(csv_file, db_config, table_name):
    print("Step 1: Reading CSV file...")
    df = read_excel(csv_file )
    print(f"Loaded {len(df)} rows")

    print("\nStep 2: Extracting additional fields...")
    df = extract_fields(df)

    print("\nStep 3: Creating column mapping...")
    mapping = create_column_mapping()

    print("\nStep 4: Renaming columns to match DB...")
    df_final = rename_columns(df, mapping)
    print(f"Final columns: {list(df_final.columns)}")

    print("\nStep 5: Generating SQL file...")
    generate_sql_file(df_final, table_name)

    print("\nDone!")
    return df_final

# Example usage
if __name__ == "__main__":
    # Configure your database connection
    db_config = {
        'host': '10.22.33.120',
        'user': 'root',
        'password': 'performance',
        'database': 'performanceroute'
    }

    # Specify your CSV file path and table name
    csv_file = r'C:\Users\o84432318\Downloads\hourly_huawe_10_17_feb.xlsx'  # Change this to your file path
    table_name = 'hourly_huawei_2g_all_counters'

    # Run the import
    df_result = main(csv_file, db_config, table_name)

    # Optional: Preview the data
    print("\nPreview of transformed data:")
    print(df_result.head())




