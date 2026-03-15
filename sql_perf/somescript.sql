CREATE TABLE `daily_2g_worst_cell_kpis` (
  `date` DATE NOT NULL,
  `cell_name` VARCHAR(100) CHARACTER SET utf8 NOT NULL,
  `bsc` VARCHAR(50) CHARACTER SET utf8 DEFAULT NULL,
  `cbr` DECIMAL(20,12) DEFAULT NULL,
  `cdr` DECIMAL(20,6) DEFAULT NULL,
  `csr` DECIMAL(20,6) DEFAULT NULL,
  PRIMARY KEY (`date`, `cell_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

select * from daily_2g_worst_cell_kpis

  DROP TABLE IF EXISTS daily_2g_worst_cell_kpis;

  DELETE FROM daily_2g_worst_cell_kpis
ORDER BY date ASC  -- ASC ensures the oldest (earliest) dates come first
LIMIT 100000;

-- CREATE TABLE
CREATE TABLE `daily_2g_worst_cell_kpis` (
  `date` DATE NOT NULL,
  `cell_name` VARCHAR(100) CHARACTER SET utf8 NOT NULL,
  `bsc` VARCHAR(50) CHARACTER SET utf8 DEFAULT NULL,

  /* high-precision KPIs (use DECIMAL(55,12) as requested) */
  `cdr` DECIMAL(20,12) DEFAULT NULL,
  `cbr` DECIMAL(20,12) DEFAULT NULL,
  `csr` DECIMAL(20,12) DEFAULT NULL,

  /* counters / aggregates (use DECIMAL(20,6) as requested) */
  `cnrelcong` DECIMAL(20,6) DEFAULT NULL,
  `ccongs` DECIMAL(20,6) DEFAULT NULL,
  `tndrop` DECIMAL(20,6) DEFAULT NULL,
  `coup_tot` DECIMAL(20,6) DEFAULT NULL,
  `nb_echecs_tch` DECIMAL(20,6) DEFAULT NULL,
  `ccr_failures` DECIMAL(20,6) DEFAULT NULL,
  `coup_sd` DECIMAL(20,6) DEFAULT NULL,

  /* weights / ratios with high precision */
  `weight_of_tchdrop` DECIMAL(55,12) DEFAULT NULL,
  `weight_congestion_tch_pct` DECIMAL(55,12) DEFAULT NULL,
  `weight_of_ccr_failures_pct` DECIMAL(55,12) DEFAULT NULL,

  PRIMARY KEY (`date`, `cell_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

desc daily_2g_worst_cell_kpis

-- show rows for 2025-09-23
SELECT *
FROM daily_2g_worst_cell_kpis
WHERE date = '2025-09-23'
ORDER BY cell_name;


SELECT 
    `date`,
    `cell_name`,
    `bsc`,
    ROUND(cdr, 4) AS cdr,
    ROUND(cbr, 4) AS cbr,
    ROUND(csr, 4) AS csr,
    CAST(cnrelcong AS SIGNED) AS cnrelcong,
    CAST(ccongs AS SIGNED) AS ccongs,
    CAST(tndrop AS SIGNED) AS tndrop,
    CAST(coup_tot AS SIGNED) AS coup_tot,
    CAST(nb_echecs_tch AS SIGNED) AS nb_echecs_tch,
    CAST(ccr_failures AS SIGNED) AS ccr_failures,
    CAST(coup_sd AS SIGNED) AS coup_sd,
    ROUND(weight_of_tchdrop * 100, 4) AS weight_of_tchdrop_pct,
    ROUND(weight_congestion_tch_pct * 100, 4) AS weight_congestion_tch_pct,
    ROUND(weight_of_ccr_failures_pct * 100, 4) AS weight_of_ccr_failures_pct
FROM daily_2g_worst_cell_kpis
WHERE date = '2025-09-28'
ORDER BY cell_name;




SELECT 
            DATE_FORMAT(t.date, '%Y-%m') AS month, 
            COALESCE(s.site, 'UNKNOWN') AS SITE_NAME,
            SUM(t.Total_Voice) AS Total_Voice
        FROM hourly_huawei_trafic_per_cell_site_2g t
        LEFT JOIN (
            SELECT CELL, MIN(site) as site
            FROM sites_and_info_2g_huawei
            GROUP BY CELL
        ) s ON t.CELL_NAME = s.CELL
        WHERE t.date BETWEEN '2025-09-10' AND '2025-11-12'
        GROUP BY DATE_FORMAT(t.date, '%Y-%m'), s.site
        ORDER BY month, s.site







-- --------------------------------------------------------------------








desc sites_and_info_4g_huawei

select * from hourly_huawei_trafic_per_cell_site_2g  limit 10  
SELECT DISTINCT site FROM hourly_huawei_trafic_per_cell_site_4g 


  
  -- hw voice 2g
SELECT 
t.date, 
COALESCE(s.site, 'UNKNOWN') AS SITE_NAME,
SUM(t.Total_Voice) AS Total_Voice
FROM hourly_huawei_trafic_per_cell_site_2g t
LEFT JOIN sites_and_info_2g_huawei s ON t.CELL_NAME = s.CELL
WHERE t.date BETWEEN '2025-10-29' AND '2025-10-29'
GROUP BY t.date, s.site
ORDER BY t.date, s.site

  -- hw data 2g

  SELECT 
  t.date, t.cell_name,
  COALESCE(s.site, 'UNKNOWN') AS SITE_NAME,
  SUM(t.Total_Data) AS Total_Data
  FROM hourly_huawei_trafic_per_cell_site_2g t
  LEFT JOIN sites_and_info_2g_huawei s ON t.CELL_NAME = s.CELL
  WHERE t.date BETWEEN '2025-11-10' AND '2025-11-12'
  GROUP BY t.date, s.site
  ORDER BY t.date, s.site
  


-- hw 3g voice
            SELECT 
            t.date, 
            COALESCE(s.site, 'UNKNOWN') AS SITE_NAME,
            SUM(t.Total_Voice) AS Total_Voice
        FROM hourly_huawei_trafic_per_cell_site_2g t
        LEFT JOIN (
            SELECT CELL, MIN(site) as site
            FROM sites_and_info_2g_huawei
            GROUP BY CELL
        ) s ON t.CELL_NAME = s.CELL
        WHERE t.date BETWEEN '2025-11-11' AND '2025-11-11'
        GROUP BY t.date, s.site
        ORDER BY t.date, s.site

  SELECT 
            t.date, 
            COALESCE(s.SITE, 'UNKNOWN') AS SITE_NAME,
            SUM(t.Total_Data) AS Total_Data
        FROM hourly_huawei_trafic_per_cell_site_4g t
        LEFT JOIN (
            SELECT cell, MIN(SITE) as SITE
            FROM sites_and_info_4g_huawei
            GROUP BY cell
        ) s ON t.CELL_NAME = s.cell
        WHERE t.date BETWEEN '2025-11-11' AND '2025-11-11'
        GROUP BY t.date, s.SITE
        ORDER BY t.date, s.SITE


  select SUM(Total_Data) AS Total_Data
  from hourly_huawei_trafic_per_cell_site_4g
  WHERE date BETWEEN '2025-11-11' AND '2025-11-11'
        select SUM(Total_Voice) AS Total_Voice 
  from hourly_huawei_trafic_per_cell_site_2g
        WHERE date BETWEEN '2025-11-11' AND '2025-11-11'
  
SELECT 
            t.date, 
            COALESCE(s.SITE, 'UNKNOWN') AS SITE_NAME,
            SUM(t.Total_data) AS Total_Voice
        FROM hourly_huawei_trafic_per_cell_site_3g t
        LEFT JOIN (
            SELECT ucell, MIN(SITE) as SITE
            FROM sites_and_info_3g_huawei
            GROUP BY ucell
        ) s ON t.CELL_NAME = s.ucell
        WHERE t.date BETWEEN '2025-11-11' AND '2025-11-11'
        GROUP BY t.date, s.SITE
        ORDER BY t.date, s.SITE
  
  select sum(total_voice ) 
  from hourly_huawei_trafic_per_cell_site_3g 
  wHERE date BETWEEN '2025-11-11' AND '2025-11-11'

  SELECT s.ucell, COUNT(*) AS cnt
FROM sites_and_info_3g_huawei s
GROUP BY s.ucell
HAVING COUNT(*) > 1;


  -- hw 3g data 

    SELECT 
                t.date, 
                COALESCE(s.SITE, 'UNKNOWN') AS SITE_NAME,
                SUM(t.Total_Data) AS Total_data
            FROM hourly_huawei_trafic_per_cell_site_3g t
            LEFT JOIN sites_and_info_3g_huawei s ON t.CELL_NAME = s.ucell
            WHERE t.date BETWEEN '2025-11-12' AND '2025-11-12'
            GROUP BY t.date, s.SITE
            ORDER BY t.date, s.SITE


            
 -- hw 4g data

  SELECT 
                t.date, 
                COALESCE(s.SITE, 'UNKNOWN') AS SITE_NAME,
                SUM(t.Total_Data) AS Total_Data
            FROM hourly_huawei_trafic_per_cell_site_4g t
            LEFT JOIN sites_and_info_4g_huawei s ON t.CELL_NAME = s.cell
            WHERE t.date BETWEEN '2025-11-12' AND '2025-11-12'
            GROUP BY t.date, s.SITE


-- "Ericsson_2G_Data": f"""
            SELECT 
                date_id AS date, 
                SITE_NAME,
                SUM(Total_Data_Volume) AS Total_Data_Volume
            FROM hourly_ericsson_trafic_per_site_2g
            WHERE date_id BETWEEN '2025-11-12' AND '2025-11-12'
            GROUP BY date_id, SITE_NAME
            ORDER BY date_id, SITE_NAME

            select SUM(Total_Data_Volume)
            FROM hourly_ericsson_trafic_per_site_2g
            WHERE date_id BETWEEN '2025-11-11' AND '2025-11-11'

            select SUM(valeur)
            FROM ericsson2g_data
            WHERE date BETWEEN '2025-11-11' AND '2025-11-11'
      
      desc ericsson2g_data

  -- "Ericsson_2G_Voice": f"""
            SELECT 
                date, 
                SITE_NAME,
                SUM(trafic2gVoix) AS trafic2gVoix
            FROM hourly_ericsson_trafic_per_site_2g_voix
            WHERE date BETWEEN '2025-11-12' AND '2025-11-12'
            GROUP BY date, SITE_NAME
            ORDER BY date, SITE_NAME


-- "Ericsson_3G_Data": f"""
SELECT 
    date_id AS date, 
    RBS_Id AS SITE_NAME,
    SUM(Total_Data_Volume) AS Total_Data_Volume
FROM hourly_ericsson_trafic_per_site_3g 
WHERE date_id BETWEEN '2025-11-12' AND '2025-11-12'
GROUP BY date_id, RBS_Id
ORDER BY date_id, RBS_Id;

-- 
-- "Ericsson_3G_Voice": f"""
SELECT 
    date, 
    RBS AS site_name, 
    SUM(trafic_3g_voix) AS trafic_3g_voix
FROM hourly_ericsson_trafic_per_site_3g_voix 
WHERE date BETWEEN '2025-11-12' AND '2025-11-12'
GROUP BY date, RBS
ORDER BY date, RBS;

-- "Ericsson_4G_Data": f"""
           SELECT 
    date, 
    ERBS_Id AS SITE_NAME,
    SUM(valeur) AS total
FROM ericsson4g_data 
WHERE date BETWEEN '2025-11-12' AND '2025-11-12'
GROUP BY date, ERBS_Id
ORDER BY date, ERBS_Id;

-- ----------------------------------------------------------------
SELECT 
    t.date, 
    t.cell_name,
    COALESCE(s.site, 'UNKNOWN') AS SITE_NAME
FROM 
    hourly_huawei_trafic_per_cell_site_2g t
LEFT JOIN 
    sites_and_info_2g_huawei s 
    ON t.CELL_NAME = s.CELL
WHERE 
    t.date BETWEEN '2025-11-10' AND '2025-11-12'
    AND s.site IS NULL  -- This ensures we're only getting rows with no match
ORDER BY 
    t.date, t.cell_name;

select 

  
  
select  * from hourly_huawei_trafic_per_cell_site_2g limit 5

  SELECT
  date_trunc('month', t.date)::date AS month_start,
  COALESCE(s.site, 'UNKNOWN') AS site_name,
  SUM(t.total_voice) AS total_voice
FROM hourly_huawei_trafic_per_cell_site_2g t
LEFT JOIN (
  SELECT cell, MIN(site) AS site
  FROM sites_and_info_2g_huawei
  GROUP BY cell
) s ON t.cell_name = s.cell
WHERE t.date BETWEEN '2022-09-10' AND '2025-11-12'
GROUP BY date_trunc('month', t.date), s.site
ORDER BY date_trunc('month', t.date), s.site;


SELECT 
            DATE_FORMAT(t.date, '%Y-%m') AS month, 
            COALESCE(s.site, 'UNKNOWN') AS SITE_NAME,
            SUM(t.Total_Voice) AS Total_Voice
        FROM hourly_huawei_trafic_per_cell_site_2g t
        LEFT JOIN (
            SELECT CELL, MIN(site) as site
            FROM sites_and_info_2g_huawei
            GROUP BY CELL
        ) s ON t.CELL_NAME = s.CELL
        WHERE t.date BETWEEN '2022-09-10' AND '2025-11-12'
        GROUP BY DATE_FORMAT(t.date, '%Y-%m'), s.site
        ORDER BY month, s.site

desc hourly_huawei_trafic_per_cell_site_2g

SELECT 
            DATE_FORMAT(date, '%Y-%m') AS month, 
            SITE_NAME,
            SUM(trafic2gVoix) AS trafic2gVoix
        FROM hourly_ericsson_trafic_per_site_2g_voix
        WHERE date BETWEEN '2022-05-10' AND '2025-11-12'
        GROUP BY DATE_FORMAT(date, '%Y-%m'), SITE_NAME
        ORDER BY month, SITE_NAME


select  SUM(Total_Voice) AS Total_Voice
FROM hourly_huawei_trafic_per_cell_site_2g
WHERE date BETWEEN '2025-10-01' AND '2025-10-31'


SELECT 
SUM(Total_Data) AS Total_Data
FROM hourly_huawei_trafic_per_cell_site_4g
WHERE date BETWEEN '2025-10-01' AND '2025-10-31'
           








