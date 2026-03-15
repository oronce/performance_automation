

import pandas as pd
import pandas as pd
import mysql.connector

df_2g_ericsson= pd.read_excel("performance_automation/assets/site_info.xlsx", sheet_name="2G_ERICSSON")
df_2g_huawei= pd.read_excel("performance_automation/assets/site_info.xlsx", sheet_name="2G_HUAWEI")
df_3g_ericsson= pd.read_excel("performance_automation/assets/site_info.xlsx", sheet_name="3G_ERICSSON")
df_3g_huawei= pd.read_excel("performance_automation/assets/site_info.xlsx", sheet_name="3G_HUAWEI")
df_4g_ericsson = pd.read_excel("performance_automation/assets/site_info.xlsx", sheet_name="4G_ERICSSON")
df_4g_huawei = pd.read_excel("performance_automation/assets/site_info.xlsx", sheet_name="4G_HUAWEI")


print()

def mis_encode(text):
    if isinstance(text, str):
        return text.encode("utf-8").decode("latin1")
    return text

df_2g_ericsson["Arrondissement "] = df_2g_ericsson["Arrondissement "].apply(mis_encode)
df_2g_huawei["arrondissement "] = df_2g_huawei["arrondissement"].apply(mis_encode)
df_3g_ericsson["ARRONDISSEMENT"] = df_3g_ericsson["ARRONDISSEMENT"].apply(mis_encode)
df_3g_huawei["ARRONDISSEMENT"] = df_3g_huawei["ARRONDISSEMENT"].apply(mis_encode)
df_4g_ericsson["Arrondissement "] = df_4g_ericsson["Arrondissement "].apply(mis_encode)
df_4g_huawei["Arrondissement "] = df_4g_huawei["Arrondissement "].apply(mis_encode)



##### 2. Connect to DB
conn = mysql.connector.connect(
    host="10.22.33.116",
    user="root",
    password="performance",
    database="performanceroute"
)

# conn = mysql.connector.connect(
#     host="10.22.33.120",
#     user="root",
#     password="root@2025",
#     database="npm_monitor"
# )

# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="performance",
#     database="local_perf"
# )

cursor = conn.cursor()

#ericsson 2g
# for _, row in df_2g_ericsson.iterrows():
    
#     print(row)
#     cursor.execute('''
#     INSERT INTO sites_and_info_2g_ericsson (site_name, bsc, arrondissement, commune, departement)
#     VALUES (%s, %s, %s, %s, %s)
#     ''', (
#         row["SITE NAME"],
#         row["BSC "],
#         row["Arrondissement "],
#         row["Commune"],
#         row["Departement"]
#     ))

#########huawei 2g
try:
    df_2g_huawei = df_2g_huawei.fillna('')
    for _, row in df_2g_huawei.iterrows():

        values = [
            row.get("GCELL"),
            row.get("cell"),
            row.get("site"),
            row.get("arrondissement"),
            row.get("zone"),
            row.get("commune"),
            row.get("departement")
        ]

        print(
            row["GCELL"],
            row["cell"],
            row["site"],
            row["arrondissement"],
            row["zone"],
            row["commune"],
            row["departement"]
        )

        #####Replace NaN with None for SQL NULL
        values = ['' if pd.isna(v) else v for v in values]
        cursor.execute('''
        REPLACE INTO sites_and_info_2g_huawei 
            (GCELL, cell, site, arrondissement, zone, commune, departement)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        
      
    ''', (
        row["GCELL"],
        row["cell"],
        row["site"],
        row["arrondissement"],
        row["zone"],
        row["commune"],
        row["departement"]
    ))

except Exception as e:
    print(f"An error occurred: {e}")        

#ericsson 3g
# for _, row in df_3g_ericsson.iterrows():
#     print(
#         row["UCell Id"],
#         row["RBS Id"],
#         row.get("RNC Id"),
#         row.get("ARRONDISSEMENT"),
#         row.get("COMMUNE")
#     )
#     cursor.execute('''
#         INSERT INTO sites_and_info_3g_ericsson
#             (UCell, RBS_Id, RNC_Id, ARRONDISSEMENT, COMMUNE)
#         VALUES (%s, %s, %s, %s, %s)
#         ON DUPLICATE KEY UPDATE
#             RNC_Id = VALUES(RNC_Id),
#             ARRONDISSEMENT = VALUES(ARRONDISSEMENT),
#             COMMUNE = VALUES(COMMUNE)
#     ''', (
#         row["UCell Id"],
#         row["RBS Id"],
#         row.get("RNC Id"),
#         row.get("ARRONDISSEMENT"),
#         row.get("COMMUNE")
#     ))

# ...existing code...

######huawei 3g
df_3g_huawei = df_3g_huawei.fillna('')
for _, row in df_3g_huawei.iterrows():
    values = [
        row.get("BSC6910UCell"),
        row.get("UCELL"),
        row.get("SITE"),
        row.get("ARRONDISSEMENT"),
        row.get("ZONE"),
        row.get("COMMUNE")
    ]
    # Replace NaN with None for SQL NULL
    values = [None if pd.isna(v) else v for v in values]
    print(*values)
    cursor.execute('''
        REPLACE INTO sites_and_info_3g_huawei
            (BSC6910UCell, UCELL, SITE, ARRONDISSEMENT, ZONE, COMMUNE)
        VALUES (%s, %s, %s, %s, %s, %s)
        
    ''', values)

#ericsson 4g
# for _, row in df_4g_ericsson.iterrows():
#     values = [
#         row.get("EUtranCell Id"),
#         row.get("ERBS Id"),
#         mis_encode(row.get("Arrondissement ")),
#         row.get("Zone"),
#         row.get("COMMUNES"),
#         row.get("DEPARTEMENT")
#     ]
#     # Replace NaN with None for SQL NULL
#     values = ['' if pd.isna(v) else v for v in values]
#     print(*values)
#     cursor.execute('''
#         INSERT INTO sites_and_info_4g_ericsson
#             (EUtranCell_Id, ERBS_Id, Arrondissement, Zone, COMMUNES, DEPARTEMENT)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         ON DUPLICATE KEY UPDATE
#             Arrondissement = VALUES(Arrondissement),
#             Zone = VALUES(Zone),
#             COMMUNES = VALUES(COMMUNES),
#             DEPARTEMENT = VALUES(DEPARTEMENT)
#     ''', values)

# #huawei 4g
# for _, row in df_4g_huawei.iterrows():
#     values = [
#         row.get("4G CELL"),                       # GCELL
#         row.get("Cell"),                          # Cell
#         row.get("SITE"),                          # SITE
#         mis_encode(row.get("Arrondissement ")),   # Arrondissement
#         row.get("Zone"),                          # Zone
#         row.get("COMMUNE"),                       # COMMUNE
#         row.get("DEPARTEMENT")                    # DEPARTEMENT
#     ]
#     # Replace NaN with None for SQL NULL
#     values = ['' if pd.isna(v) else v for v in values]
#     print(*values)
#     cursor.execute('''
#         INSERT INTO sites_and_info_4g_huawei
#             (GCELL, Cell, SITE, Arrondissement, Zone, COMMUNE, DEPARTEMENT)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#         ON DUPLICATE KEY UPDATE
#             Cell = VALUES(Cell),
#             SITE = VALUES(SITE),
#             Arrondissement = VALUES(Arrondissement),
#             Zone = VALUES(Zone),
#             COMMUNE = VALUES(COMMUNE),
#             DEPARTEMENT = VALUES(DEPARTEMENT)
#     ''', values)




# 5. Commit and close
conn.commit()
conn.close()
