import pandas as pd
import mysql.connector

df = pd.read_excel(
    "performance_automation/laod_data_stuff/assets/excel_files/Adjacent Node ID_Updated.xlsx",
    sheet_name="3G"
)

df = df.fillna('')

conn = mysql.connector.connect(
    host="10.22.33.116",
    user="root",
    password="performance",
    database="performanceroute"
)

cursor = conn.cursor()

for _, row in df.iterrows():
    values = [
        row.get("Adjacent Node ID"),
        row.get("RNC_ADJNODE"),
        row.get("Adjacent Node Name"),
        row.get("Site Name"),
        row.get("RNC")
    ]
    values = ['' if pd.isna(v) else v for v in values]
    print(*values)
    cursor.execute('''
        REPLACE INTO huawei_adjacent_node_id_3g
            (adjacent_node_id, rnc_adjnode, adjacent_node_name, site_name, rnc)
        VALUES (%s, %s, %s, %s, %s)
    ''', values)

conn.commit()
conn.close()

print("Done.")