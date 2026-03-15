import pandas as pd
import sys
import os

def filter_lai_data_by_dates(input_file, output_file=None, dates_to_keep=[3, 9, 10]):
    """
    Filter LAI data to:
    1. Keep only rows where LAI ends with 1 or 2 digits (0-99)
    2. Keep only specific dates (by day of month)
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file (optional, defaults to input_file with '_filtered' suffix)
        dates_to_keep: List of day numbers to keep (default: [3, 9, 10])
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_filtered_dates.xlsx"
    
    print(f"Loading data from: {input_file}")
    
    # Load the Excel file
    df = pd.read_excel(input_file, sheet_name='Sheet1')
    
    print(f"Original data shape: {df.shape}")
    print(f"Original rows: {len(df)}")
    
    # Convert Date column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Extract day of month
    df['Day'] = df['Date'].dt.day
    
    # Keep only the date part (remove time)
    df['Date'] = df['Date'].dt.date
    
    print(f"\nUnique dates in file: {sorted(df['Day'].unique())}")
    print(f"Filtering for days: {dates_to_keep}")
    
    # Filter by dates
    df_date_filtered = df[df['Day'].isin(dates_to_keep)].copy()
    
    print(f"\nAfter date filtering:")
    print(f"  Rows: {len(df_date_filtered)} (removed {len(df) - len(df_date_filtered)})")
    
    # Convert LAI to string and get last three digits
    df_date_filtered['LAI_str'] = df_date_filtered['LAI'].astype(str)
    df_date_filtered['last_three_digits'] = df_date_filtered['LAI_str'].str[-3:].astype(int)
    
    # Filter: Keep only LAIs where last three digits < 100 (i.e., 0-99)
    filtered_df = df_date_filtered[df_date_filtered['last_three_digits'] < 100].copy()
    
    # Remove helper columns
    filtered_df = filtered_df.drop(['LAI_str', 'last_three_digits', 'Day'], axis=1)
    
    print("\n" + "="*80)
    print(f"Final filtered data shape: {filtered_df.shape}")
    print(f"Final rows: {len(filtered_df)}")
    print(f"Total rows removed: {len(df) - len(filtered_df)}")
    
    # Show breakdown by date
    print("\nRows per date in filtered data:")
    date_counts = filtered_df.groupby('Date').size()
    for date, count in date_counts.items():
        print(f"  {date}: {count} rows")
    
    print("\nSample of filtered data:")
    print(filtered_df.head(10))
    
    # Save to new Excel file
    filtered_df.to_excel(output_file, index=False, sheet_name='Sheet1')
    print(f"\n✓ Filtered data saved to: {output_file}")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Total rows processed: {len(df)}")
    print(f"  Rows kept (dates {dates_to_keep} + 1-2 digit LAI endings): {len(filtered_df)}")
    print(f"  Rows removed: {len(df) - len(filtered_df)}")
    print(f"  Output file: {output_file}")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python filter_lai_by_dates.py <input_file.xlsx> [output_file.xlsx] [dates...]")
        print("\nExamples:")
        print("  python filter_lai_by_dates.py LU_LAC_WISE.xlsx")
        print("  python filter_lai_by_dates.py LU_LAC_WISE.xlsx output.xlsx")
        print("  python filter_lai_by_dates.py LU_LAC_WISE.xlsx output.xlsx 3 9 10")
        print("  python filter_lai_by_dates.py LU_LAC_WISE.xlsx output.xlsx 1 2 3 4 5")
        print("\nDefault: Filters for dates 3, 9, and 10")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Parse arguments
    if len(sys.argv) == 2:
        # Only input file provided
        output_file = None
        dates = [3, 9, 10]
    elif len(sys.argv) == 3:
        # Input file and output file provided
        output_file = sys.argv[2]
        dates = [3, 9, 10]
    else:
        # Input file, output file, and dates provided
        output_file = sys.argv[2]
        try:
            dates = [int(d) for d in sys.argv[3:]]
        except ValueError:
            print("Error: Dates must be integers!")
            sys.exit(1)
    
    filter_lai_data_by_dates(input_file, output_file, dates)
