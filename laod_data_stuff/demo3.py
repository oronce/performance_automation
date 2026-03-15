###3G counters 1


import pandas as pd
import numpy as np



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
    
    # Replace NIL with None
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
        
        # RRC Attempted Connection Establishment
        'RRC.AttConnEstab.OrgConvCall (None)': 'RRC_AttConnEstab_OrgConvCall',
        'RRC.AttConnEstab.OrgStrCall (None)': 'RRC_AttConnEstab_OrgStrCall',
        'RRC.AttConnEstab.OrgInterCall (None)': 'RRC_AttConnEstab_OrgInterCall',
        'RRC.AttConnEstab.OrgBkgCall (None)': 'RRC_AttConnEstab_OrgBkgCall',
        'RRC.AttConnEstab.OrgSubCall (None)': 'RRC_AttConnEstab_OrgSubCall',
        'RRC.AttConnEstab.TmConvCall (None)': 'RRC_AttConnEstab_TmConvCall',
        'RRC.AttConnEstab.TmStrCall (None)': 'RRC_AttConnEstab_TmStrCall',
        'RRC.AttConnEstab.TmInterCall (None)': 'RRC_AttConnEstab_TmInterCall',
        'RRC.AttConnEstab.TmBkgCall (None)': 'RRC_AttConnEstab_TmBkgCall',
        'RRC.AttConnEstab.EmgCall (None)': 'RRC_AttConnEstab_EmgCall',
        'RRC.AttConnEstab.OrgHhPrSig (None)': 'RRC_AttConnEstab_OrgHhPrSig',
        'RRC.AttConnEstab.OrgLwPrSig (None)': 'RRC_AttConnEstab_OrgLwPrSig',
        'RRC.AttConnEstab.CallReEst (None)': 'RRC_AttConnEstab_CallReEst',
        'RRC.AttConnEstab.TmHhPrSig (None)': 'RRC_AttConnEstab_TmHhPrSig',
        'RRC.AttConnEstab.TmLwPrSig (None)': 'RRC_AttConnEstab_TmLwPrSig',
        'RRC.AttConnEstab.Unknown (None)': 'RRC_AttConnEstab_Unknown',
        
        # RRC Successful Connection Establishment
        'RRC.SuccConnEstab.OrgConvCall (None)': 'RRC_SuccConnEstab_OrgConvCall',
        'RRC.SuccConnEstab.OrgSubCall (None)': 'RRC_SuccConnEstab_OrgSubCall',
        'RRC.SuccConnEstab.TmConvCall (None)': 'RRC_SuccConnEstab_TmConvCall',
        'RRC.SuccConnEstab.EmgCall (None)': 'RRC_SuccConnEstab_EmgCall',
        'RRC.SuccConnEstab.CallReEst (None)': 'RRC_SuccConnEstab_CallReEst',
        'RRC.SuccConnEstab.Unkown (None)': 'RRC_SuccConnEstab_Unkown',
        
        # RRC Rejection
        'VS.RRC.Rej.Code.Cong (None)': 'VS_RRC_Rej_Code_Cong',
        'VS.RRC.Rej.DLCE.Cong (None)': 'VS_RRC_Rej_DLCE_Cong',
        'VS.RRC.Rej.DLPower.Cong (None)': 'VS_RRC_Rej_DLPower_Cong',
        
        # RAB Normal Release
        'VS.RAB.NormRel.CS (None)': 'VS_RAB_NormRel_CS',
        'VS.RAB.NormRel.PS (None)': 'VS_RAB_NormRel_PS',
        'VS.RAB.NormRel.CS.HSPA.Conv (None)': 'VS_RAB_NormRel_CS_HSPA_Conv',
        'VS.RAB.NormRel.AMRWB (None)': 'VS_RAB_NormRel_AMRWB',
        'VS.RAB.NormRel.PS.PCH (None)': 'VS_RAB_NormRel_PS_PCH',
        
        # RAB Abnormal Release
        'VS.RAB.AbnormRel.PS (None)': 'VS_RAB_AbnormRel_PS',
        'VS.RAB.AbnormRel.AMR (None)': 'VS_RAB_AbnormRel_AMR',
        'VS.RAB.AbnormRel.CS.HSPA.Conv (None)': 'VS_RAB_AbnormRel_CS_HSPA_Conv',
        'VS.RAB.AbnormRel.AMRWB (None)': 'VS_RAB_AbnormRel_AMRWB',
        'VS.RAB.AbnormRel.PS.PCH (None)': 'VS_RAB_AbnormRel_PS_PCH',
        'VS.RAB.AbnormRel.PS.F2P (None)': 'VS_RAB_AbnormRel_PS_F2P',
        'VS.RAB.AbnormRel.PS.D2P (None)': 'VS_RAB_AbnormRel_PS_D2P',
        
        # RAB Attempted Establishment CS
        'VS.RAB.AttEstabCS.Conv (None)': 'VS_RAB_AttEstabCS_Conv',
        'VS.RAB.AttEstabCS.Str (None)': 'VS_RAB_AttEstabCS_Str',
        'VS.RAB.AttEstab.AMR (None)': 'VS_RAB_AttEstab_AMR',
        'VS.RAB.AttEstabCS.AMRWB (None)': 'VS_RAB_AttEstabCS_AMRWB',
        
        # RAB Successful Establishment CS
        'VS.RAB.SuccEstabCS.Conv (None)': 'VS_RAB_SuccEstabCS_Conv',
        'VS.RAB.SuccEstabCS.Str (None)': 'VS_RAB_SuccEstabCS_Str',
        'VS.RAB.SuccEstabCS.AMR (None)': 'VS_RAB_SuccEstabCS_AMR',
        'VS.RAB.SuccEstabCS.AMRWB (None)': 'VS_RAB_SuccEstabCS_AMRWB',
        
        # RAB Failed Establishment CS
        'VS.RAB.FailEstabCS.Code.Cong (None)': 'VS_RAB_FailEstabCS_Code_Cong',
        'VS.RAB.FailEstabCS.DLCE.Cong (None)': 'VS_RAB_FailEstabCS_DLCE_Cong',
        'VS.RAB.FailEstabCS.ULCE.Cong (None)': 'VS_RAB_FailEstabCS_ULCE_Cong',
        'VS.RAB.FailEstabCS.ULIUBBand.Cong (None)': 'VS_RAB_FailEstabCS_ULIUBBand_Cong',
        'VS.RAB.FailEstabCS.DLIUBBand.Cong (None)': 'VS_RAB_FailEstabCS_DLIUBBand_Cong',
        'VS.RAB.FailEstabCS.ULPower.Cong (None)': 'VS_RAB_FailEstabCS_ULPower_Cong',
        'VS.RAB.FailEstabCS.DLPower.Cong (None)': 'VS_RAB_FailEstabCS_DLPower_Cong',
        
        # RAB Failed Establishment PS
        'VS.RAB.FailEstabPS.Code.Cong (None)': 'VS_RAB_FailEstabPS_Code_Cong',
        'VS.RAB.FailEstabPS.DLCE.Cong (None)': 'VS_RAB_FailEstabPS_DLCE_Cong',
        
        # HSPA RAB
        'VS.HSPA.RAB.AttEstab.CS.Conv (None)': 'VS_HSPA_RAB_AttEstab_CS_Conv',
        'VS.HSPA.RAB.SuccEstab.CS.Conv (None)': 'VS_HSPA_RAB_SuccEstab_CS_Conv',
        
        # DCCC
        'VS.DCCC.Succ.F2P (None)': 'VS_DCCC_Succ_F2P',
        'VS.DCCC.D2P.Succ (None)': 'VS_DCCC_D2P_Succ',
        
        # Cell Unavailability
        'VS.Cell.UnavailTime.Sys (s)': 'VS_Cell_UnavailTime_Sys',
        
        # Traffic
        'Total PS Traffic(GB) (%)': 'Total_PS_Traffic_GB',
    }
    return mapping

# Step 4: Rename columns to match DB
def rename_columns(df, mapping):
    existing_cols = [col for col in mapping.keys() if col in df.columns]
    df_mapped = df[existing_cols].copy()
    df_mapped.rename(columns=mapping, inplace=True)
    return df_mapped

# Step 5: Generate SQL files with row limit per file
def generate_sql_file(df, table_name, output_file='insert_data.sql', batch_size=5000, max_rows_per_file=500000):

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
                    # Format values
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            escaped = val.replace("'", "\\'")
                            values.append(f"'{escaped}'")
                        else:
                            values.append(f"'{val}'")

                    row_str = '(' + ', '.join(values) + ')'

                    if idx < len(batch_df) - 1:
                        f.write(f"    {row_str},\n")
                    else:
                        f.write(f"    {row_str};\n\n")

                print(f"  Progress: {min(i+batch_size, len(df_file))}/{len(df_file)} rows written")

        print(f"File {file_counter} completed: {file_end - file_start} rows")
        file_counter += 1

    print(f"\nAll files generated successfully!")

# Main execution
def main(excel_file, table_name, output_sql):
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
    
    print("\nStep 5: Generating SQL file...")
    generate_sql_file(df_final, table_name, output_sql, batch_size=5000)
    
    print("\nDone!")
    return df_final

# Example usage
if __name__ == "__main__":
    excel_file = r'C:\Users\o84432318\Downloads\HOURLY_3G_ALL_COUNTERS_1(2026-01-06 185147)_20260106_193937.csv'
    table_name = 'hourly_huawei_3g_all_counters_1'
    output_sql = 'excel_output/insert_3g_counters.sql'
    
    df_result = main(excel_file, table_name, output_sql)