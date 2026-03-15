# def format_phone_number(phone_number):
#     numeric_only = ''.join(filter(str.isdigit, phone_number))
#     groups = [numeric_only[i:i+3] for i in range(0, len(numeric_only), 3)]
#     formatted_number = ' '.join(groups)
#     return formatted_number

# while True:
#     input_number = input("Enter the phone number (or 'q' to quit): ")
    
#     if input_number.lower() == 'q':
#         print("Exiting the app.")
#         break
    
#     formatted_number = format_phone_number(input_number)
#     print("Formatted phone number:", formatted_number)
    
 
# import pandas as pd
# from datetime import datetime
# from nt_report_perf.abstract_class.base_report import data_manager , DbOperations  , base_db_utils , Datetime ,chart_manager, Weekly_datetime_manager , fill_to_excel_native2 ,fill_to_excel_native3 , fill_to_excel_one_by_one , general_utilities


# ##read a sheet from an excel file without format header to datetime just give the column name

# df = pd.read_excel(r"C:\Users\RYAN\Downloads\SMSMOTrafic_destinations22082023.xlsx" , sheet_name="Sheet3" , )
# df = df.set_index('network')

# col = df.columns

# #format header to date format exemple day/month/year
# #df.columns = pd.to_datetime()
# new_col = []
# for col in df.columns:
    
#     if type(col) != str:
#         col = col.strftime("%d/%m/%Y")
#         #date_datetime = date_datetime.date()
#     else:
#         #we convert the str date to datetime and then to  ("%d/%m/%Y") format
#         date_datetime = datetime.strptime(col, '%d/%m/%y') 
#         col=str(date_datetime.strftime("%d/%m/%Y"))
#     new_col.append(col)    
    
# df.columns = new_col

# #reconvert the date to datetime format
# datetime_str_cols = df.columns
# new_col = []
# for col in datetime_str_cols:
#     date_datetime = (datetime.strptime(col, '%d/%m/%Y') )
#     date_datetime = date_datetime.strftime("%Y/%m/%d")
#     new_col.append(date_datetime)
# df.columns = new_col
    
# print() 

# from faker import Faker
# fake = Faker()

# # Generate 10 random names and addresses
# for _ in range(10):
#     name = fake.name()
#     address = fake.address()
#     print(f"Name: {name}, Address: {address}\n")


import random
from datetime import datetime, timedelta

def generate_timestamps(start_time, end_time, min_interval=10, max_interval=20):
    timestamps = [start_time]
    current_time = start_time

    while current_time < end_time:
        interval = random.randint(min_interval, max_interval)
        current_time += timedelta(seconds=interval)
        if current_time < end_time:
            timestamps.append(current_time)
    
    return timestamps

# Define the start and end times
start_time = datetime.strptime("15:23:20", "%H:%M:%S")
end_time = datetime.strptime("15:45:00", "%H:%M:%S")

# Generate the timestamps
timestamps = generate_timestamps(start_time, end_time)

# Print the timestamps
for ts in timestamps:
    print(ts.strftime("%H:%M:%S"))
