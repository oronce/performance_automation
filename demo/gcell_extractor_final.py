import mysql.connector
import pandas as pd
from datetime import datetime
import sys

# Try to import config, otherwise use defaults
try:
    from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DATE_START, DATE_END, OUTPUT_FILE
except ImportError:
    print("Warning: config.py not found, using default values")
    DB_HOST = "localhost"
    DB_USER = "your_username"
    DB_PASSWORD = "your_password"
    DB_NAME = "your_database"
    DATE_START = "2025-12-08"
    DATE_END = "2025-12-08"
    OUTPUT_FILE = "gcell_results.xlsx"

# Database configuration
DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME
}

# Site and Cell mapping for 2G
SITE_CELL_2G = {
    'PARAKOU_26': ['PAR261', 'PAR262', 'PAR263'],
    'PARAKOU_27': ['PAR271', 'PAR272', 'PAR273'],
    'PARAKOU_29': ['PAR291', 'PAR292', 'PAR293'],
    'R_GOUGNIROU': ['GOUGN1'],
    'R_BORO': ['BORO1'],
    'R_BONROU': ['BONRO1'],
    'R_WARI': ['WARI1'],
    'PARAKOU_40': ['PAR401', 'PAR402', 'PAR403'],
    'PARAKOU_33': ['PAR331', 'PAR332', 'PAR333'],
    'PARAKOU_43': ['PAR431', 'PAR432', 'PAR433'],
    'PARAKOU_36': ['PAR361', 'PAR362', 'PAR363'],
    'PARAKOU_34': ['PAR341', 'PAR342', 'PAR343'],
    'PARAKOU_25': ['PAR251', 'PAR252', 'PAR253'],
    'PARAKOU_35': ['PAR351', 'PAR352', 'PAR353']
}

# Site and Cell mapping for 3G
SITE_CELL_3G = {
    'PARAKOU_26': ['UPAR267', 'UPAR268', 'UPAR269'],
    'PARAKOU_27': ['UPAR277', 'UPAR278', 'UPAR279'],
    'PARAKOU_29': ['UPAR297', 'UPAR298', 'UPAR299'],
    'R_GOUGNIROU': ['UGOUGN7'],
    'R_BORO': ['UBORO7'],
    'R_BONROU': ['UBONRO7'],

    'R_WARI': ['UWARI7'],
    'PARAKOU_40': ['UPAR407', 'UPAR408', 'UPAR409'],
    'PARAKOU_33': ['UPAR337', 'UPAR338', 'UPAR339'],
    'PARAKOU_43': ['UPAR437', 'UPAR438', 'UPAR439'],
    'PARAKOU_36': ['UPAR367', 'UPAR368', 'UPAR369'],
    'PARAKOU_34': ['UPAR347', 'UPAR348', 'UPAR349'],
    'PARAKOU_25': ['UPAR257', 'UPAR258', 'UPAR259'],
    'PARAKOU_35': ['UPAR357', 'UPAR358', 'UPAR359']
}

def get_gcell_2g(cursor, cell_names, date_start, date_end):
    """Extract GCELL information for 2G cell names"""
    if not cell_names:
        return {}
    
    cell_list = "', '".join(cell_names)
    
    query = f"""
    SELECT DISTINCT 
        ucell as gcell,
        SUBSTRING_INDEX(SUBSTRING_INDEX(ucell, 'LABEL=', -1), ',', 1) as cell_name
    FROM hourly_arcep_huawei_2g
    WHERE date BETWEEN '{date_start}' AND '{date_end}'
    AND SUBSTRING_INDEX(SUBSTRING_INDEX(ucell, 'LABEL=', -1), ',', 1) IN ('{cell_list}')
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    gcell_map = {}
    for gcell, cell_name in results:
        if cell_name not in gcell_map:
            gcell_map[cell_name] = gcell
    
    return gcell_map

def get_gcell_3g(cursor, cell_names, date_start, date_end):
    """Extract GCELL information for 3G cell names"""
    if not cell_names:
        return {}
    
    cell_list = ', '.join([f"'{cell}'" for cell in cell_names])

    query = f"""

    SELECT  SUBSTRING(gcell, LOCATE('Label=', gcell)) AS `gcell` , cell_name
FROM hourly_huawei_3g_all_counters_1
where date BETWEEN '{date_start}' AND '{date_end}'
and cell_name in ({cell_list}) ;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    gcell_map = {}
    for gcell, cell_name in results:
        if cell_name not in gcell_map:
            gcell_map[cell_name] = gcell
    
    return gcell_map

def extract_all_gcells(date_start, date_end):
    """Extract GCELL information for all sites - both 2G and 3G"""
    
    # Connect to database
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to database successfully\n")
    except mysql.connector.Error as err:
        print(f"✗ Database connection error: {err}")
        sys.exit(1)
    
    results = []
    
    print(f"Extracting GCELL data from {date_start} to {date_end}")
    print("=" * 70)
    
    # Process 2G cells
    print("\n[2G CELLS]")
    print("-" * 70)
    for site_name, cell_names in SITE_CELL_2G.items():
        if not cell_names:
            continue
        
        print(f"\nSite: {site_name} ({len(cell_names)} cells)")
        
        try:
            gcell_map = get_gcell_2g(cursor, cell_names, date_start, date_end)
            
            for cell_name in cell_names:
                gcell = gcell_map.get(cell_name, 'NOT_FOUND')
                results.append({
                    'Site_Name': site_name,
                    'Technology': '2G',
                    'Cell_Name': cell_name,
                    'GCELL': gcell
                })
                
                if gcell == 'NOT_FOUND':
                    print(f"  ✗ {cell_name}: NOT FOUND")
                else:
                    print(f"  ✓ {cell_name}: {gcell}")
        except Exception as e:
            print(f"  ✗ Error processing site {site_name}: {e}")
    
    # Process 3G cells
    print("\n\n[3G CELLS]")
    print("-" * 70)
    for site_name, cell_names in SITE_CELL_3G.items():
        if not cell_names:
            continue
        
        print(f"\nSite: {site_name} ({len(cell_names)} cells)")
        
        try:
            gcell_map = get_gcell_3g(cursor, cell_names, date_start, date_end)
            
            for cell_name in cell_names:
                gcell = gcell_map.get(cell_name, 'NOT_FOUND')
                results.append({
                    'Site_Name': site_name,
                    'Technology': '3G',
                    'Cell_Name': cell_name,
                    'GCELL': gcell
                })
                
                if gcell == 'NOT_FOUND':
                    print(f"  ✗ {cell_name}: NOT FOUND")
                else:
                    print(f"  ✓ {cell_name}: {gcell}")
        except Exception as e:
            print(f"  ✗ Error processing site {site_name}: {e}")
    
    cursor.close()
    conn.close()
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("-" * 70)
    print(f"Total sites: {len(set(df['Site_Name']))}")
    print(f"Total cells: {len(results)}")
    
    # Summary by technology
    for tech in ['2G', '3G']:
        tech_df = df[df['Technology'] == tech]
        found = len(tech_df[tech_df['GCELL'] != 'NOT_FOUND'])
        total = len(tech_df)
        not_found = total - found
        print(f"{tech}: {found}/{total} cells found, {not_found} NOT FOUND")
    
    return df

def export_to_excel(df, output_file):
    """Export results to Excel file"""
    try:
        df.to_excel(output_file, index=False, sheet_name='GCELL_Data')
        print(f"\n✓ Results exported to: {output_file}")
    except Exception as e:
        print(f"\n✗ Error exporting to Excel: {e}")

def main():
    """Main execution function"""
    
    print("\n" + "=" * 70)
    print(" GCELL EXTRACTION TOOL - 2G & 3G")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print(f"  Date range: {DATE_START} to {DATE_END}")
    print(f"  Output file: {OUTPUT_FILE}\n")
    
    # Extract GCELL data
    df = extract_all_gcells(DATE_START, DATE_END)
    
    # Export to Excel
    export_to_excel(df, OUTPUT_FILE)
    
    # Display detailed summary
    print("\n" + "=" * 70)
    print("DETAILED SUMMARY BY SITE:")
    print("=" * 70)
    
    for site in sorted(df['Site_Name'].unique()):
        site_df = df[df['Site_Name'] == site]
        
        # 2G summary
        site_2g = site_df[site_df['Technology'] == '2G']
        found_2g = len(site_2g[site_2g['GCELL'] != 'NOT_FOUND'])
        total_2g = len(site_2g)
        
        # 3G summary
        site_3g = site_df[site_df['Technology'] == '3G']
        found_3g = len(site_3g[site_3g['GCELL'] != 'NOT_FOUND'])
        total_3g = len(site_3g)
        
        print(f"\n{site}:")
        if total_2g > 0:
            print(f"  2G: {found_2g}/{total_2g} cells found")
        if total_3g > 0:
            print(f"  3G: {found_3g}/{total_3g} cells found")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
