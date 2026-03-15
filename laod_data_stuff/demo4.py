import pandas as pd
import numpy as np

# Step 1: Read the Excel file
def read_excel(file_path):
    df = pd.read_csv(file_path)
    return df

# Step 2: Extract additional fields from Cell column
def extract_fields(df):
    # Extract SITE_NAME: everything before first '/'
    df['SITE_NAME'] = df['NE Name'].str.split('/').str[0]
    
    # Extract CELL_NAME: third element after splitting by comma, then take what's after '='
    df['CELL_NAME'] = df['Cell'].str.split(',').str[2].str.split('=').str[-1]
    
    # Extract eNodeB_Func_Name: first element after comma, then take what's after '='
    #df['eNodeB_Func_Name'] = df['Cell'].str.split(',').str[0].str.split('=').str[-1]
    df['eNodeB_Func_Name'] = df['Cell'].str.split('eNodeB Function Name=').str[1].str.split(',').str[0]
    
    # Extract eNodeB_ID: second-to-last element after '=', then take what's before comma
    df['eNodeB_ID'] = df['Cell'].str.split('=').str[-2].str.split(',').str[0]
    
    # Extract local_cell_id: second element after comma, then take what's after '='
    df['local_cell_id'] = df['Cell'].str.split(',').str[1].str.split('=').str[-1]
    
    # Extract date and time from Start Time
    df['date'] = pd.to_datetime(df['Start Time']).dt.date
    df['time'] = pd.to_datetime(df['Start Time']).dt.time
    
    # Rename Cell to GCELL
    df['GCELL'] = df['NE Name'] + '/Cell:' + df['Cell']
    
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
        'SITE_NAME': 'SITE_NAME',
        'CELL_NAME': 'CELL_NAME',
        'eNodeB_Func_Name': 'eNodeB_Func_Name',
        'eNodeB_ID': 'eNodeB_ID',
        'local_cell_id': 'local_cell_id',
        
        # Handover - Intra eNodeB Intra Frequency
        'L.HHO.IntraeNB.IntraFreq.PrepAttOut (None)': 'L_HHO_IntraeNB_IntraFreq_PrepAttOut',
        'L.HHO.IntraeNB.IntraFreq.ExecAttOut (None)': 'L_HHO_IntraeNB_IntraFreq_ExecAttOut',
        'L.HHO.IntraeNB.IntraFreq.ExecSuccOut (None)': 'L_HHO_IntraeNB_IntraFreq_ExecSuccOut',
        
        # Handover - Intra eNodeB Inter Frequency
        'L.HHO.IntraeNB.InterFreq.PrepAttOut (None)': 'L_HHO_IntraeNB_InterFreq_PrepAttOut',
        'L.HHO.IntraeNB.InterFreq.ExecAttOut (None)': 'L_HHO_IntraeNB_InterFreq_ExecAttOut',
        'L.HHO.IntraeNB.InterFreq.ExecSuccOut (None)': 'L_HHO_IntraeNB_InterFreq_ExecSuccOut',
        
        # Handover - Inter eNodeB Intra Frequency
        'L.HHO.IntereNB.IntraFreq.PrepAttOut (None)': 'L_HHO_IntereNB_IntraFreq_PrepAttOut',
        'L.HHO.IntereNB.IntraFreq.ExecAttOut (None)': 'L_HHO_IntereNB_IntraFreq_ExecAttOut',
        'L.HHO.IntereNB.IntraFreq.ExecSuccOut (None)': 'L_HHO_IntereNB_IntraFreq_ExecSuccOut',
        
        # Handover - Inter eNodeB Inter Frequency
        'L.HHO.IntereNB.InterFreq.PrepAttOut (None)': 'L_HHO_IntereNB_InterFreq_PrepAttOut',
        'L.HHO.IntereNB.InterFreq.ExecAttOut (None)': 'L_HHO_IntereNB_InterFreq_ExecAttOut',
        'L.HHO.IntereNB.InterFreq.ExecSuccOut (None)': 'L_HHO_IntereNB_InterFreq_ExecSuccOut',
        
        # Handover - Inter eNodeB Inter FDD/TDD
        'L.HHO.IntereNB.InterFddTdd.PrepAttOut (None)': 'L_HHO_IntereNB_InterFddTdd_PrepAttOut',
        'L.HHO.IntereNB.InterFddTdd.ExecAttOut (None)': 'L_HHO_IntereNB_InterFddTdd_ExecAttOut',
        'L.HHO.IntereNB.InterFddTdd.ExecSuccOut (None)': 'L_HHO_IntereNB_InterFddTdd_ExecSuccOut',
        
        # Cell Unavailability
        'L.Cell.Unavail.Dur.Sys (s)': 'L_Cell_Unavail_Dur_Sys',
        'L.Cell.Unavail.Dur.Manual (s)': 'L_Cell_Unavail_Dur_Manual',
        
        # E-RAB
        'L.E-RAB.SuccEst (None)': 'L_E_RAB_SuccEst',
        'L.E-RAB.AttEst (None)': 'L_E_RAB_AttEst',
        'L.E-RAB.AbnormRel (None)': 'L_E_RAB_AbnormRel',
        'L.E-RAB.NormRel (None)': 'L_E_RAB_NormRel',
        
        # RRC Connection Request Attempted
        'L.RRC.ConnReq.Att.Emc (None)': 'L_RRC_ConnReq_Att_Emc',
        'L.RRC.ConnReq.Att.HighPri (None)': 'L_RRC_ConnReq_Att_HighPri',
        'L.RRC.ConnReq.Att.Mt (None)': 'L_RRC_ConnReq_Att_Mt',
        'L.RRC.ConnReq.Att.MoData (None)': 'L_RRC_ConnReq_Att_MoData',
        
        # RRC Connection Request Successful
        'L.RRC.ConnReq.Succ.Emc (None)': 'L_RRC_ConnReq_Succ_Emc',
        'L.RRC.ConnReq.Succ.HighPri (None)': 'L_RRC_ConnReq_Succ_HighPri',
        'L.RRC.ConnReq.Succ.Mt (None)': 'L_RRC_ConnReq_Succ_Mt',
        'L.RRC.ConnReq.Succ.MoData (None)': 'L_RRC_ConnReq_Succ_MoData',
        
        # Throughput
        'L.Thrp.bits.UL (bit)': 'L_Thrp_bits_UL',
        'L.Thrp.bits.DL (bit)': 'L_Thrp_bits_DL',
        'L.Thrp.bits.DL.LastTTI (bit)': 'L_Thrp_bits_DL_LastTTI',
        'L.Thrp.bits.UE.UL.LastTTI (bit)': 'L_Thrp_bits_UE_UL_LastTTI',
        'L.Thrp.Time.Cell.DL.HighPrecision (ms)': 'L_Thrp_Time_Cell_DL_HighPrecision',
        'L.Thrp.Time.Cell.UL.HighPrecision (ms)': 'L_Thrp_Time_Cell_UL_HighPrecision',
        'L.Thrp.Time.DL.RmvLastTTI (ms)': 'L_Thrp_Time_DL_RmvLastTTI',
        'L.Thrp.Time.UE.UL.RmvLastTTI (ms)': 'L_Thrp_Time_UE_UL_RmvLastTTI',
        
        # CSFB
        'L.CSFB.PrepAtt (None)': 'L_CSFB_PrepAtt',
        'L.CSFB.E2G (None)':'L_CSFB_E2G',
        'L.CSFB.E2W (None)': 'L_CSFB_E2W',
        'L.CSFB.PrepSucc (None)': 'L_CSFB_PrepSucc',
        'L.RRCRedirection.E2W.CSFB (None)': 'L_RRCRedirection_E2W_CSFB',
        'L.RRCRedirection.E2G.CSFB (None)': 'L_RRCRedirection_E2G_CSFB',
        'L.IRATHO.E2W.CSFB.ExecAttOut (None)': 'L_IRATHO_E2W_CSFB_ExecAttOut',
        'L.IRATHO.E2W.CSFB.ExecSuccOut (None)': 'L_IRATHO_E2W_CSFB_ExecSuccOut',
        'L.IRATHO.E2G.CSFB.ExecAttOut (None)': 'L_IRATHO_E2G_CSFB_ExecAttOut',
        'L.IRATHO.E2G.CSFB.ExecSuccOut (None)': 'L_IRATHO_E2G_CSFB_ExecSuccOut',
        
        # Traffic
        '4G TOTAL LTE TRAFFIC Huawei (Gbits)': 'TOTAL_DATA_GBITS',
    }
    return mapping

# Step 4: Rename columns to match DB
def rename_columns(df, mapping):
    existing_cols = [col for col in mapping.keys() if col in df.columns]
    df_mapped = df[existing_cols].copy()
    df_mapped.rename(columns=mapping, inplace=True)
    return df_mapped


# Step 5: Generate SQL files with row limit per file
def generate_sql_file(df, table_name, output_file='excel_output/insert_data.sql', batch_size=5000, max_rows_per_file=500000):
    
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
    excel_file = r'C:\Users\o84432318\Downloads\ExportPerformanceQueryResult_HOURLY_4G_ALL_COUNTERS_11_20260128_204736\ExportPerformanceQueryResult_HOURLY_4G_ALL_COUNTERS_11_20260128_204736_2.csv'  # Change this to your file path
    
    table_name = 'hourly_huawei_4g_all_counters_1'
    output_sql = 'excel_output/insert_4g_counters.sql'
    
    df_result = main(excel_file, table_name, output_sql)