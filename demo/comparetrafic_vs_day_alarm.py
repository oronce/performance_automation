import pandas as pd
import mysql.connector
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': '10.22.33.116',
    'user': 'root',
    'password': 'performance',
    'database': 'performanceroute'
}

def execute_query_with_dates(dat, dat2):
    """
    Execute SQL query with two date parameters

    Args:
        dat: First date (format: 'YYYY-MM-DD')
        dat2: Second date (format: 'YYYY-MM-DD')

    Returns:
        pandas.DataFrame: Query results
    """

    # Sample SQL query - REPLACE THIS WITH YOUR ACTUAL QUERY
    query = f"""


   SET @dat='{dat}' , @dat2='{dat2}';
WITH  
  t2g_voix AS (
 -- SET @dat='2025-05-21' , @dat2='2025-05-21';
    SELECT date,  heur, ROUND(SUM(valeur),2) AS voix_2g_ericsson
    FROM ericsson2g_voix
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, heur
  ),
  t2g_hv AS (
 
    SELECT date, TIME AS heur, ROUND(SUM(Total_Voice),2) AS voix_2g_huawei
    FROM hourly_huawei_trafic_per_cell_site_2g
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, TIME
  ),
  t3g_voix AS (
    SELECT date, heur, ROUND(SUM(valeur),2) AS voix_3g_ericsson
    FROM  ericsson3g_voix
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, heur
    ),
   t3g_hv AS (
      SELECT date, TIME AS heur, ROUND(SUM(Total_Voice),2) AS voix_3g_huawei
    FROM hourly_huawei_trafic_per_cell_site_3g
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, TIME
    ),
      t2g_data AS (
    SELECT date, heur, ROUND(SUM(valeur),2) AS data_2g_ericsson
    FROM ericsson2g_data
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, heur
  ),
    t2g_hd AS (
    SELECT date, TIME AS heur, ROUND(SUM(Total_Data),2) AS data_2g_huawei
    FROM  hourly_huawei_trafic_per_cell_site_2g
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, TIME
  ),
       t3g_data AS (
    SELECT date, heur, ROUND(SUM(Total_Data_Volume),2) AS data_3g_ericsson
    FROM  ericsson3g_data
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, heur
  ),
    t3g_hd AS (
    SELECT date, TIME AS heur, ROUND(SUM(Total_Data),2) AS data_3g_huawei
    FROM  hourly_huawei_trafic_per_cell_site_3g
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, TIME
  ),
     t4g_data AS (
    SELECT date, heur, ROUND(SUM(valeur),2) AS data_4g_ericsson
    FROM   ericsson4g_data
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, heur
  ),
    t4g_hd AS (
    SELECT date, TIME AS heur, ROUND(SUM(Total_Data),2) AS data_4g_huawei
    FROM  hourly_huawei_trafic_per_cell_site_4g
    WHERE date BETWEEN @dat AND @dat2
    GROUP BY date, TIME
  ),
  
-- les BSC et RNC
controller_raw AS (
-- SET @dat='2025-05-27' , @dat2='2025-05-27';
   SELECT DATE,HOUR(STR_TO_DATE(heur, '%H:%i:%s')) AS heur,bsc controler, round(SUM(CAST(valeur AS DECIMAL(10,2)))) AS total_voice_controller,'BSC_' AS node FROM  ericsson2g_voix WHERE date BETWEEN @dat AND @dat2
   GROUP by DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')),bsc
  UNION ALL
-- SET @dat='2025-05-27' , @dat2='2025-05-27';
	SELECT DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) , rnc , round(SUM(CAST(valeur AS DECIMAL(10,2)))) ,'RNC_' FROM ericsson3g_voix WHERE date BETWEEN @dat AND @dat2 GROUP by DATE, DATE_FORMAT(STR_TO_DATE(heur, '%H'), '%H:00'),rnc
    UNION ALL 
-- SET @dat='2025-05-27' , @dat2='2025-05-27';
    SELECT date, HOUR(STR_TO_DATE(time, '%H:%i:%s')) ,controller, ROUND(SUM(Total_Voice),2), 'BSC_' FROM hourly_huawei_trafic_per_cell_site_2g WHERE date BETWEEN @dat AND @dat2 GROUP BY date, TIME,controller
     UNION all
    SELECT date, HOUR(STR_TO_DATE(time, '%H:%i:%s')) ,controller, ROUND(SUM(Total_Voice),2),'RNC_'  FROM hourly_huawei_trafic_per_cell_site_3g WHERE date BETWEEN @dat AND @dat2 GROUP BY date, TIME,controller
),

controler_stat AS (
       -- BSCs
       SELECT DATE,heur, 
       SUM(case when controler='BHBSC03' then total_voice_controller ELSE 0 END)  AS 'BHBSC03',
		 SUM(case when controler='BHBSC04' then total_voice_controller ELSE 0 END)  AS 'BHBSC04',
	    SUM(	case when controler='BHBSC05' then total_voice_controller ELSE 0 END)  AS 'BHBSC05',
 		SUM(case when controler='HQBSC01' then total_voice_controller ELSE 0 END)  AS 'HQBSC01',
 		SUM(case when controler='HQBSC02' then total_voice_controller ELSE 0 END)  AS 'HQBSC02',
 		SUM(case when controler='HQBSC03' then total_voice_controller ELSE 0 END)  AS 'HQBSC03',
		SUM(case when controler='PKBSC06' then total_voice_controller ELSE 0 END)  AS 'PKBSC06',
  		SUM(case when controler='PKBSC07' then total_voice_controller ELSE 0 END) AS 'PKBSC07',
  		SUM(case when controler='PKMBSC01' and node ='BSC_' then total_voice_controller ELSE 0 END) AS 'PKMBSC01',
  		SUM(case when controler='PKMBSC03' and node ='BSC_' then total_voice_controller ELSE 0 END) AS 'PKMBSC03',
  		-- RNCs

		  SUM(case when controler='BHRNC03' then total_voice_controller ELSE 0 END)  AS 'BHRNC03',
		 SUM(case when controler='BHRNC04' then total_voice_controller ELSE 0 END)  AS 'BHRNC04',
	    SUM(	case when controler='HQRNC01' then total_voice_controller ELSE 0 END)  AS 'HQRNC01',
 		SUM(case when controler='HQRNC03' then total_voice_controller ELSE 0 END)  AS 'HQRNC03',
 		SUM(case when controler='HQRNC04' then total_voice_controller ELSE 0 END)  AS 'HQRNC04',
 		SUM(case when controler='PKRNC02' then total_voice_controller ELSE 0 END)  AS 'PKRNC02',
		SUM(case when controler='BHRNC05' then total_voice_controller ELSE 0 END)  AS 'BHRNC05',
  		SUM(case when controler='PKRNC03' then total_voice_controller ELSE 0 END) AS 'PKRNC03',
  		SUM(case when controler='PKMBSC01' and node ='RNC_' then total_voice_controller ELSE 0 END) AS 'PKMBSC01_RNC',
  		SUM(case when controler='PKMBSC03' and node ='RNC_' then total_voice_controller ELSE 0 END) AS 'PKMBSC03_RNC'
		 FROM controller_raw WHERE  date BETWEEN @dat AND @dat2
		 GROUP BY DATE,heur
		 ),
--  SELECT *
--  FROM controler_stat
  /* idem pour t3g_voix, t2g_data, t3g_data, t4g_data… */
  /*w*/
  

    
  -- union de toutes les voix
  voix_temp AS (
    SELECT DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, voix_2g_ericsson AS voix, 'ericsson' AS SOURCE, '2g' AS techno FROM t2g_voix
    UNION ALL
    SELECT DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, voix_2g_huawei, 'huawei', '2g' FROM t2g_hv
    UNION ALL 
    SELECT DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, voix_3g_ericsson , 'ericsson','3g'  FROM t3g_voix
    UNION ALL
    SELECT date, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, voix_3g_huawei, 'huawei','3g' FROM t3g_hv
  
  ),
  -- union de toutes les datas
  datas AS (
    SELECT DATE, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, data_2g_ericsson AS data, 'ericsson'  AS SOURCE ,'2g' AS techno FROM t2g_data
    UNION ALL
    SELECT date, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, data_2g_huawei, 'huawei' ,'2g'  FROM t2g_hd
    UNION ALL 
    SELECT date, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, data_3g_ericsson , 'ericsson' ,'3g' FROM t3g_data
    UNION ALL
    SELECT date, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, data_3g_huawei, 'huawei' ,'3g' FROM t3g_hd
    UNION ALL 
    SELECT date, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, data_4g_ericsson , 'ericsson','4g'  FROM t4g_data
     UNION ALL
    SELECT date, HOUR(STR_TO_DATE(heur, '%H:%i:%s')) heur, data_4g_huawei, 'huawei' ,'4g' FROM t4g_hd

 
  ),
  
  voix_stat AS (
  SELECT date,heur ,SUM(voix) 'Total_voice',
  ROUND(SUM(CASE WHEN source = 'ericsson' THEN voix ELSE 0 END), 2) AS `Total_voice_Ericsson`,
  ROUND(SUM(CASE WHEN source = 'huawei' THEN voix ELSE 0 END), 2) AS `Total_voice_Huawei`,
  ROUND(SUM(CASE WHEN techno = '2g' THEN voix ELSE 0 END), 2) AS `Total_voice_2G`,
  ROUND(SUM(CASE WHEN techno = '3g' THEN voix ELSE 0 END), 2) AS `Total_voice_3G`,
 -- ROUND(SUM(CASE WHEN techno = '2g' THEN voix ELSE 0 END), 2) AS `Total_voice_2G`,
  ROUND(SUM(CASE WHEN techno = '2g' AND SOURCE='huawei' THEN voix ELSE 0 END), 2) AS `Voice_2G_huawei`,
  ROUND(SUM(CASE WHEN techno = '3g' AND SOURCE='huawei' THEN voix ELSE 0 END), 2) AS `Voice_3G_huawei`,
  ROUND(SUM(CASE WHEN techno = '2g' AND SOURCE='ericsson' THEN voix ELSE 0 END), 2) AS `Voice_2G_ericsson`,
  ROUND(SUM(CASE WHEN techno = '3g' AND SOURCE='ericsson' THEN voix ELSE 0 END), 2) AS `Voice_3G_ericsson`
  FROM voix_temp
  GROUP BY DATE,heur
  ),
  
  data_stat AS ( SELECT date,heur ,SUM(data) 'Total_data',
  ROUND(SUM(CASE WHEN source = 'ericsson' THEN data ELSE 0 END), 2) AS `Total_data_Ericsson`,
  ROUND(SUM(CASE WHEN source = 'huawei' THEN data ELSE 0 END), 2) AS `Total_data_Huawei`,
  ROUND(SUM(CASE WHEN techno = '2g' THEN data ELSE 0 END), 2) AS `Total_data_2G`,
  ROUND(SUM(CASE WHEN techno = '3g' THEN data ELSE 0 END), 2) AS `Total_data_3G`,
  ROUND(SUM(CASE WHEN techno = '4g' THEN data ELSE 0 END), 2) AS `Total_data_4G`,
  ROUND(SUM(CASE WHEN techno = '2g' AND source = 'ericsson' THEN data ELSE 0 END), 2) AS `Data_2G_ericsson`,
  ROUND(SUM(CASE WHEN techno = '3g' AND source = 'ericsson' THEN data ELSE 0 END), 2) AS `Data_3G_ericsson`,
  ROUND(SUM(CASE WHEN techno = '4g' AND source = 'ericsson' THEN data ELSE 0 END), 2) AS `Data_4G_ericsson`,
  ROUND(SUM(CASE WHEN techno = '2g' AND source = 'huawei' THEN data ELSE 0 END), 2) AS `Data_2G_huawei`,
  ROUND(SUM(CASE WHEN techno = '3g' AND source = 'huawei' THEN data ELSE 0 END), 2) AS `Data_3G_huawei`,
  ROUND(SUM(CASE WHEN techno = '4g' AND source = 'huawei' THEN data ELSE 0 END), 2) AS `Data_4G_huawei`
  FROM datas
  GROUP BY DATE,heur
  )
  
SELECT
  v.date,
   v.heur,
   v.Total_voice,Total_voice_2G,Total_voice_3G,
   d.Total_data,Total_data_2G,Total_data_3G,Total_data_4G,
   Total_voice_Ericsson,Voice_2G_ericsson,Voice_3G_ericsson,
  Total_voice_Huawei,Voice_2G_huawei,Voice_3G_huawei,
  Total_data_Ericsson,Data_2G_ericsson,Data_3G_ericsson,Data_4G_ericsson
  ,Total_data_Huawei,Data_2G_huawei,Data_3G_huawei,Data_4G_huawei,
  BHBSC03,BHBSC04,BHBSC05,HQBSC01,HQBSC02,HQBSC03,PKBSC06,PKBSC07,PKMBSC01,PKMBSC03,BHRNC03,BHRNC04,HQRNC01,HQRNC03,HQRNC04,PKRNC02,BHRNC05,PKRNC03,PKMBSC01_RNC,PKMBSC03_RNC
FROM voix_stat v
LEFT JOIN data_stat d ON v.date = d.date  AND v.heur = d.heur
LEFT JOIN controler_stat c ON v.date =c.date  AND v.heur = c.heur
GROUP BY v.date  , v.heur
ORDER BY v.date  , v.heur;

  



    """

    # Execute query with multi-statement support
    conn = mysql.connector.connect(**DB_CONFIG)

    # Split and execute statements manually
    # First execute the SET statement
    cursor = conn.cursor()
    cursor.execute(f"SET @dat='{dat}', @dat2='{dat2}'")
    cursor.close()

    # Now execute the main CTE query (everything after SET)
    # Remove the SET statement from query
    main_query = query.split('WITH', 1)[1]  # Get everything after SET
    main_query = 'WITH' + main_query  # Add WITH back

    # Execute the main query and get results as DataFrame
    df = pd.read_sql(main_query, conn)

    conn.close()

    return df


def process_dataframe(df):
    """
    Process the dataframe - ADD YOUR PROCESSING LOGIC HERE

    Args:
        df: pandas.DataFrame from query results

    Returns:
        pandas.DataFrame: Processed dataframe
    """

    # Example processing - REPLACE WITH YOUR ACTUAL LOGIC
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())

    # Add your pandas processing here
    # Example: Calculate daily averages
    # df_daily = df.groupby(['DATE', 'SITE_NAME']).agg({
    #     'VOICE_TRAFFIC': 'mean',
    #     'DATA_TRAFFIC': 'mean'
    # }).reset_index()

    return df


def main(dat, dat2):
    """
    Main function to execute query and process results

    Args:
        dat: First date (format: 'YYYY-MM-DD')
        dat2: Second date (format: 'YYYY-MM-DD')
    """
    print(f"Fetching data from {dat} to {dat2}...")

    # Execute query
    df = execute_query_with_dates(dat, dat2)

    print(f"\nProcessing dataframe...")

    # Process dataframe
    df_processed = process_dataframe(df)

    print("\nDone!")
    return df_processed


if __name__ == "__main__":
    # Example usage
    dat = "2025-12-10"
    dat2 = "2025-12-12"

    result_df = main(dat, dat2)
