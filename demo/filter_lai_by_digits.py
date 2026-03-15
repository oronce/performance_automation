import pandas as pd
import sys
import os

def filter_lai_data(input_file, output_file=None):
    """
    Filter LAI data to keep only rows where LAI ends with 1 or 2 digits (0-99).
    Removes rows where LAI ends with 3 or more digits (100+).
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file (optional, defaults to input_file with '_filtered' suffix)
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_filtered.xlsx"
    
    print(f"Loading data from: {input_file}")
    
    # Load the Excel file
    df = pd.read_excel(input_file, sheet_name='Sheet1')
    
    print(f"Original data shape: {df.shape}")
    print(f"Original rows: {len(df)}")
    print("\nSample of original LAI values:")
    print(df['LAI'].head(20).tolist())
    
    # Convert LAI to string and get last three digits
    df['LAI_str'] = df['LAI'].astype(str)
    df['last_three_digits'] = df['LAI_str'].str[-3:].astype(int)
    
    # Filter: Keep only LAIs where last three digits < 100 (i.e., 0-99)
    # This keeps 1-digit endings (00-09) and 2-digit endings (10-99)
    # This removes 3-digit endings (100-999)
    filtered_df = df[df['last_three_digits'] < 100].copy()
    
    # Remove helper columns
    filtered_df = filtered_df.drop(['LAI_str', 'last_three_digits'], axis=1)
    
    print("\n" + "="*80)
    print(f"Filtered data shape: {filtered_df.shape}")
    print(f"Filtered rows: {len(filtered_df)}")
    print(f"Rows removed: {len(df) - len(filtered_df)}")
    
    print("\nSample of filtered LAI values (ending with 1 or 2 digits):")
    print(filtered_df['LAI'].head(30).tolist())
    
    print("\nFirst 10 rows of filtered data:")
    print(filtered_df.head(10))
    
    # Save to new Excel file
    filtered_df.to_excel(output_file, index=False, sheet_name='Sheet1')
    print(f"\n✓ Filtered data saved to: {output_file}")
    
    # Show some statistics about what was removed
    removed_df = df[df['last_three_digits'] >= 100]
    if len(removed_df) > 0:
        print(f"\nSample of removed LAIs (ending with 3 digits, 100+):")
        unique_removed = removed_df['LAI'].unique()
        print(unique_removed[:20])
    else:
        print("\nNo LAIs with 3-digit endings found in the data.")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Total rows processed: {len(df)}")
    print(f"  Rows kept (1-2 digit endings): {len(filtered_df)}")
    print(f"  Rows removed (3+ digit endings): {len(df) - len(filtered_df)}")
    print(f"  Output file: {output_file}")


if __name__ == "__main__":
    # Check command line arguments

    print("Usage: python filter_lai_by_digits.py <input_file.xlsx> [output_file.xlsx]")
    print("\nExample:")
    print("  python filter_lai_by_digits.py LU_LAC_WISE.xlsx")
    print("  python filter_lai_by_digits.py LU_LAC_WISE.xlsx LU_LAC_WISE_filtered.xlsx")
    
    input_file = r"C:\Users\OLOKO\Downloads\LU_LAC_WISE.xlsx"
    output_file = r"excel_output\LU_LAC_WISE_filtered.xlsx" 
    
    filter_lai_data(input_file, output_file)

    print("\nProcessing complete.")
