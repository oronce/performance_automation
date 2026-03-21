import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DB_CONFIG = {
    'host': '10.22.33.120',
    'user': 'root',
    'password': 'root@2025',
    'database': 'npm_monitor'
}

# Column mapping: Excel headers -> SQL table columns
COLUMN_MAPPINGS = {
    'EPT 2G': {
        'excel_to_sql': {
            'VENDOR': 'VENDOR',
            'CELL NAME': 'CELL_NAME',
            'SITE NAME': 'SITE_NAME',
            'BSC': 'BSC',
            'BCCH': 'BCCH',
            'BSIC': 'BSIC',
            'CELL ID': 'CELL_ID',
            'LAC': 'LAC',
            'FREQUENCE': 'FREQUENCE',
            'AZIMUTH': 'AZIMUTH',
            'LONGITUDE': 'LONGITUDE',
            'LATITUDE': 'LATITUDE',
            'Arrondissement': 'ARRONDISSEMENT',
            'Commune': 'COMMUNE',
            'DEPARTEMENT': 'DEPARTEMENT'
        },
        'table_name': 'EPT_2G'
    },
    'EPT 3G': {
        'excel_to_sql': {
            'VENDOR': 'VENDOR',
            'UCell NAME': 'CELL_NAME',
            'RBS NAME': 'RBS_NAME',
            'SITE NAME': 'SITE_NAME',
            'RNC': 'RNC',
            'LAC': 'LAC',
            'localcellid': 'localcellid',
            'ServiceArea': 'ServiceArea',
            'PSC': 'PSC',
            'FREQ BAND': 'FREQ_BAND',
            'BANDE': 'BANDE',
            'AZIMUTH': 'AZIMUTH',
            'LONGITUDE': 'LONGITUDE',
            'LATITUDE': 'LATITUDE',
            'Arrondissement': 'ARRONDISSEMENT',
            'Commune': 'COMMUNE',
            'DEPARTEMENT': 'DEPARTEMENT'
        },
        'table_name': 'EPT_3G'
    },
    'EPT 4G': {
        'excel_to_sql': {
            'VENDOR': 'VENDOR',
            'EUtranCell Name': 'CELL_NAME',
            'ERBS Id': 'ERBS_Id',
            'SITE NAME 4G': 'SITE_NAME',
            'enbid': 'enodb_id',
            'TAC': 'TAC',
            'cellid': 'cell_id',
            'dlchannelbandwidth': 'dlchannelbandwidth',
            'earfcndl': 'earfcndl',
            'earfcnul': 'earfcnul',
            'freqband': 'freq_band',
            'PCI': 'PCI',
            'ulchannelbandwidth': 'ulchannelbandwidth',
            'Bande': 'Bande',
            'AZIMUTH': 'AZIMUTH',
            'LONGITUDE': 'LONGITUDE',
            'LATITUDE': 'LATITUDE',
            'Arrondissement': 'ARRONDISSEMENT',
            'Commune': 'COMMUNE',
            'DEPARTEMENT': 'DEPARTEMENT'
        },
        'table_name': 'EPT_4G'
    },
    'EPT 5G': {
        'excel_to_sql': {
            'Vendor': 'VENDOR',
            'NRCellDUId': 'CELL_NAME',
            'gNode B name': 'gNodeB_name',
            'Site Name': 'SITE_NAME',
            'gNBId': 'gNBId',
            'cellLocalId': 'cellLocalId',
            'nRPCI': 'nRPCI',
            'nRTAC': 'nRTAC',
            'NRSectorCarrierId': 'NRSectorCarrierId',
            'arfcnDL': 'arfcnDL',
            'arfcnUL': 'arfcnUL',
            'bSChannelBwDL': 'bSChannelBwDL',
            'AZIMUTH': 'AZIMUTH',
            'LONGITUDE': 'LONGITUDE',
            'LATITUDE': 'LATITUDE',
            'Arrondissement': 'ARRONDISSEMENT',
            'Commune': 'COMMUNE',
            'DEPARTEMENT': 'DEPARTEMENT'
        },
        'table_name': 'EPT_5G'
    }
}


def validate_headers(df, expected_mapping, sheet_name):
    """Validate that Excel headers match expected columns"""
    excel_headers = set(df.columns.str.strip())
    expected_headers = set(expected_mapping.keys())
    
    missing = expected_headers - excel_headers
    extra = excel_headers - expected_headers
    
    if missing:
        logging.warning(f"Sheet '{sheet_name}': Missing columns: {missing}")
    if extra:
        logging.warning(f"Sheet '{sheet_name}': Extra columns (will be ignored): {extra}")
    
    return len(missing) == 0


def clean_dataframe(df, column_mapping):
    """Clean and prepare dataframe for insertion"""
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Keep only columns that exist in mapping
    available_cols = [col for col in column_mapping.keys() if col in df.columns]
    df = df[available_cols].copy()
    
    # Rename columns to match SQL table
    rename_dict = {k: v for k, v in column_mapping.items() if k in available_cols}
    df.rename(columns=rename_dict, inplace=True)
    
    # Replace NaN with None for SQL NULL
    df = df.where(pd.notna(df), None)
    
    # Strip whitespace from string values
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    return df


def insert_data_batch(cursor, table_name, df, batch_size=1000):
    """Insert data in batches with duplicate handling"""
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))

    # REPLACE INTO for updating existing records
    sql = f"REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"

    total_rows = len(df)
    inserted = 0

    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i + batch_size]
        data = [tuple(row) for row in batch.values]

        cursor.executemany(sql, data)
        inserted += cursor.rowcount
        logging.info(f"Batch {i//batch_size + 1}: Processed {len(batch)} rows, Affected {cursor.rowcount} rows")

    return inserted


def load_excel_to_sql(excel_file, db_config):
    """Main function to load Excel data into SQL tables"""
    try:
        # Read Excel file
        logging.info(f"Reading Excel file: {excel_file}")
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        # excel_data = excel_data.fillna('')

        # Connect to database
        logging.info("Connecting to database...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Process each sheet
        for sheet_name, config in COLUMN_MAPPINGS.items():
            if sheet_name not in excel_data:
                logging.warning(f"Sheet '{sheet_name}' not found in Excel file")
                continue
            
            logging.info(f"\n{'='*60}")
            logging.info(f"Processing sheet: {sheet_name}")
            logging.info(f"Target table: {config['table_name']}")
            
            df = excel_data[sheet_name]
            df = df.fillna('')
            logging.info(f"Total rows in sheet: {len(df)}")
            
            # Validate headers
            if not validate_headers(df, config['excel_to_sql'], sheet_name):
                logging.error(f"Header validation failed for sheet '{sheet_name}'. Skipping...")
                continue
            
            # Clean and prepare data
            df_clean = clean_dataframe(df, config['excel_to_sql'])
            logging.info(f"Rows after cleaning: {len(df_clean)}")
            
            if df_clean.empty:
                logging.warning(f"No data to insert for sheet '{sheet_name}'")
                continue
            
            # Insert data
            inserted = insert_data_batch(cursor, config['table_name'], df_clean)
            connection.commit()
            logging.info(f"Successfully inserted {inserted} rows into {config['table_name']}")
        
        cursor.close()
        connection.close()
        logging.info("\n" + "="*60)
        logging.info("Data loading completed successfully!")
        
    except FileNotFoundError:
        logging.error(f"Excel file not found: {excel_file}")
    except Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Configuration
    EXCEL_FILE = "performance_automation/laod_data_stuff/assets/excel_files/EPT.xlsx"  # Update with your file path
    
    # Update DB_CONFIG with your credentials
    DB_CONFIG['host'] = '10.22.33.116'
    DB_CONFIG['user'] = 'root'
    DB_CONFIG['password'] = 'performance'
    DB_CONFIG['database'] = 'performanceroute'
    
    # Run the loader
    load_excel_to_sql(EXCEL_FILE, DB_CONFIG)