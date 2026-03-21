 
 
 select date  , cell_name   , count(cell_name) number_of_downtime
  FROM 
 (
 SELECT
      e.DATE,
       e.TIME,
      e.CELL_NAME,
      -- ept.SITE_NAME,
      -- ept.ARRONDISSEMENT,
      -- ept.COMMUNE,
      -- ept.DEPARTEMENT,

      -- CSSR (Call Setup Success Rate) - ERICSSON
      CASE
        WHEN COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) = 0
          OR (COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
            ) = 0
        THEN 0
        ELSE
          100.0
          * (1.0 - (SUM(CAST(CCONGS AS DOUBLE))
                     / SUM(CAST(CCALLS AS DOUBLE))))
          * (1.0 - ((SUM(CAST(CNDROP AS DOUBLE))
                      - SUM(CAST(CNRELCONG AS DOUBLE)))
                     / SUM(CAST(CMSESTAB AS DOUBLE))))
          * (SUM(CAST(TCASSALL AS DOUBLE))
              / SUM(CAST(TASSALL AS DOUBLE)))
          * (1.0 - (
              (SUM(CAST(TFNDROP AS DOUBLE))
                + SUM(CAST(THNDROP AS DOUBLE))
                + SUM(CAST(TFNDROPSUB AS DOUBLE))
                + SUM(CAST(THNDROPSUB AS DOUBLE))
              )
              / (
                SUM(CAST(TFCASSALL AS DOUBLE))
                + SUM(CAST(THCASSALL AS DOUBLE))
                + SUM(CAST(TFCASSALLSUB AS DOUBLE))
                + SUM(CAST(THCASSALLSUB AS DOUBLE))
              )
            ))
      END AS CSSR_ERICSSON,

      -- Call Blocking Rate - ERICSSON (ARCEP)
      100.0 * (
        COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
      ) / NULLIF(COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0), 0) AS CBR_ERICSSON,

      -- Call Drop Rate - ERICSSON (ARCEP)
      100.0 * (
        COALESCE(SUM(CAST(THNDROP AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNDROPSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNDROP AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNDROPSUB AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0),
        0
      ) AS CDR_ERICSSON,

      -- 2G Cell Availability Rate - ERICSSON
      100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0), 0)) AS CELL_AVAILABILITY_RATE_ERICSSON,

      -- TCH Channel Availability Rate - ERICSSON (Vendor-specific)
      100.0 * (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TAVASCAN AS DOUBLE)), 0), 0)) /
        (COALESCE(AVG(CAST(AVG_TNUCHCNT AS DOUBLE)), 1)) AS TCH_AVAILABILITY_RATE_ERICSSON,

      -- Downtime Manual - ERICSSON (Vendor-specific)
      COALESCE(SUM(CAST(HDWNACC AS DOUBLE)), 0) AS DOWNTIME_MANUAL,

      -- TCH Congestion Rate - ERICSSON
      100.0 * (
        COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
      ) / NULLIF(COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0), 0) AS TCH_CONGESTION_RATE_ERICSSON,

      -- SDCCH Drop Rate - ERICSSON
      100.0 * COALESCE(SUM(CAST(CNDROP AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_ERICSSON,

      -- SDCCH Traffic - ERICSSON (Erlangs)
      COALESCE(SUM(CAST(CTRALACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CNSCAN AS DOUBLE)), 0), 0) AS SDCCH_TRAFFIC_ERICSSON,

      -- SDCCH Blocking Rate - ERICSSON (Vendor-specific)
      100.0 * COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0), 0) AS SDCCH_BLOCKING_RATE_ERICSSON,

      -- SDCCH Congestion Rate - ERICSSON
      100.0 * (COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) + COALESCE(SUM(CAST(CCONGSSUB AS DOUBLE)), 0)) /
        NULLIF(COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_ERICSSON,

      COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) TRAFFIC_DATA_GB_ERICSSON,
      COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) TRAFFIC_VOIX_ERICSSON,
      
       CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end downtime_sec
  
      

    FROM
      hourly_ericsson_arcep_2g_counters e
    -- LEFT JOIN
    --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

    WHERE
      e.DATE BETWEEN '2026-02-19' AND '2026-02-19'  -- Adjust date range as needed

    GROUP BY
      e.DATE,
       e.TIME,
       e.CELL_NAME
      -- ept.SITE_NAME,

      having  CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end > 1800
   
   -- HAVING  (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0)) < 4860
   
  -- DESC 
 ) t1


GROUP BY date , cell_name 









######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
 ###include all site 
 ###include all site 
 ###include all site 
 ###include all site 

select date   , SITE_NAME   , count(SITE_NAME) number_of_downtime

FROM
(

 select date  ,time, ept.SITE_NAME   , avg(downtime_sec) avg_down_per_site

  FROM 
 (
 SELECT
      e.DATE,
        e.TIME,
      e.CELL_NAME,
      -- ept.SITE_NAME,
      -- ept.ARRONDISSEMENT,
      -- ept.COMMUNE,
      -- ept.DEPARTEMENT,

      -- CSSR (Call Setup Success Rate) - ERICSSON
      CASE
        WHEN COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) = 0
          OR (COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
            ) = 0
        THEN 0
        ELSE
          100.0
          * (1.0 - (SUM(CAST(CCONGS AS DOUBLE))
                     / SUM(CAST(CCALLS AS DOUBLE))))
          * (1.0 - ((SUM(CAST(CNDROP AS DOUBLE))
                      - SUM(CAST(CNRELCONG AS DOUBLE)))
                     / SUM(CAST(CMSESTAB AS DOUBLE))))
          * (SUM(CAST(TCASSALL AS DOUBLE))
              / SUM(CAST(TASSALL AS DOUBLE)))
          * (1.0 - (
              (SUM(CAST(TFNDROP AS DOUBLE))
                + SUM(CAST(THNDROP AS DOUBLE))
                + SUM(CAST(TFNDROPSUB AS DOUBLE))
                + SUM(CAST(THNDROPSUB AS DOUBLE))
              )
              / (
                SUM(CAST(TFCASSALL AS DOUBLE))
                + SUM(CAST(THCASSALL AS DOUBLE))
                + SUM(CAST(TFCASSALLSUB AS DOUBLE))
                + SUM(CAST(THCASSALLSUB AS DOUBLE))
              )
            ))
      END AS CSSR_ERICSSON,

      -- Call Blocking Rate - ERICSSON (ARCEP)
      100.0 * (
        COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
      ) / NULLIF(COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0), 0) AS CBR_ERICSSON,

      -- Call Drop Rate - ERICSSON (ARCEP)
      100.0 * (
        COALESCE(SUM(CAST(THNDROP AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNDROPSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNDROP AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNDROPSUB AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0),
        0
      ) AS CDR_ERICSSON,

      -- 2G Cell Availability Rate - ERICSSON
      100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0), 0)) AS CELL_AVAILABILITY_RATE_ERICSSON,

      -- TCH Channel Availability Rate - ERICSSON (Vendor-specific)
      100.0 * (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TAVASCAN AS DOUBLE)), 0), 0)) /
        (COALESCE(AVG(CAST(AVG_TNUCHCNT AS DOUBLE)), 1)) AS TCH_AVAILABILITY_RATE_ERICSSON,

      -- Downtime Manual - ERICSSON (Vendor-specific)
      COALESCE(SUM(CAST(HDWNACC AS DOUBLE)), 0) AS DOWNTIME_MANUAL,

      -- TCH Congestion Rate - ERICSSON
      100.0 * (
        COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
      ) / NULLIF(COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0), 0) AS TCH_CONGESTION_RATE_ERICSSON,

      -- SDCCH Drop Rate - ERICSSON
      100.0 * COALESCE(SUM(CAST(CNDROP AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_ERICSSON,

      -- SDCCH Traffic - ERICSSON (Erlangs)
      COALESCE(SUM(CAST(CTRALACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CNSCAN AS DOUBLE)), 0), 0) AS SDCCH_TRAFFIC_ERICSSON,

      -- SDCCH Blocking Rate - ERICSSON (Vendor-specific)
      100.0 * COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0), 0) AS SDCCH_BLOCKING_RATE_ERICSSON,

      -- SDCCH Congestion Rate - ERICSSON
      100.0 * (COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) + COALESCE(SUM(CAST(CCONGSSUB AS DOUBLE)), 0)) /
        NULLIF(COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_ERICSSON,

      COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) TRAFFIC_DATA_GB_ERICSSON,
      COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) TRAFFIC_VOIX_ERICSSON,
      
       CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end downtime_sec
  
      

    FROM
      hourly_ericsson_arcep_2g_counters e
    -- LEFT JOIN
    --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

    WHERE
      e.DATE BETWEEN '2026-02-12' AND '2026-02-19'  -- Adjust date range as needed

    GROUP BY
      e.DATE,
       e.TIME,
       e.CELL_NAME
      -- ept.SITE_NAME,

  --     having  CASE
  -- WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
  --  THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
  --  ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end > 1800
   
   
  -- DESC 
 ) t1
 LEFT JOIN
    EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

   

GROUP BY date ,time , ept.SITE_NAME
-- , cell_name 
  HAVING avg(downtime_sec) > 1800
)
t1


GROUP BY date , site_name 

















######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
######################################################
###only cell < 1800



select date   , SITE_NAME   , count(SITE_NAME) number_of_downtime

FROM
(

 select date  ,time, ept.SITE_NAME   , avg(downtime_sec) avg_down_per_site

  FROM 
 (
 SELECT
      e.DATE,
        e.TIME,
      e.CELL_NAME,
      -- ept.SITE_NAME,
      -- ept.ARRONDISSEMENT,
      -- ept.COMMUNE,
      -- ept.DEPARTEMENT,

      -- CSSR (Call Setup Success Rate) - ERICSSON
      CASE
        WHEN COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) = 0
          OR (COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
            ) = 0
        THEN 0
        ELSE
          100.0
          * (1.0 - (SUM(CAST(CCONGS AS DOUBLE))
                     / SUM(CAST(CCALLS AS DOUBLE))))
          * (1.0 - ((SUM(CAST(CNDROP AS DOUBLE))
                      - SUM(CAST(CNRELCONG AS DOUBLE)))
                     / SUM(CAST(CMSESTAB AS DOUBLE))))
          * (SUM(CAST(TCASSALL AS DOUBLE))
              / SUM(CAST(TASSALL AS DOUBLE)))
          * (1.0 - (
              (SUM(CAST(TFNDROP AS DOUBLE))
                + SUM(CAST(THNDROP AS DOUBLE))
                + SUM(CAST(TFNDROPSUB AS DOUBLE))
                + SUM(CAST(THNDROPSUB AS DOUBLE))
              )
              / (
                SUM(CAST(TFCASSALL AS DOUBLE))
                + SUM(CAST(THCASSALL AS DOUBLE))
                + SUM(CAST(TFCASSALLSUB AS DOUBLE))
                + SUM(CAST(THCASSALLSUB AS DOUBLE))
              )
            ))
      END AS CSSR_ERICSSON,

      -- Call Blocking Rate - ERICSSON (ARCEP)
      100.0 * (
        COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
      ) / NULLIF(COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0), 0) AS CBR_ERICSSON,

      -- Call Drop Rate - ERICSSON (ARCEP)
      100.0 * (
        COALESCE(SUM(CAST(THNDROP AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNDROPSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNDROP AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNDROPSUB AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0),
        0
      ) AS CDR_ERICSSON,

      -- 2G Cell Availability Rate - ERICSSON
      100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0), 0)) AS CELL_AVAILABILITY_RATE_ERICSSON,

      -- TCH Channel Availability Rate - ERICSSON (Vendor-specific)
      100.0 * (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TAVASCAN AS DOUBLE)), 0), 0)) /
        (COALESCE(AVG(CAST(AVG_TNUCHCNT AS DOUBLE)), 1)) AS TCH_AVAILABILITY_RATE_ERICSSON,

      -- Downtime Manual - ERICSSON (Vendor-specific)
      COALESCE(SUM(CAST(HDWNACC AS DOUBLE)), 0) AS DOWNTIME_MANUAL,

      -- TCH Congestion Rate - ERICSSON
      100.0 * (
        COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
      ) / NULLIF(COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0), 0) AS TCH_CONGESTION_RATE_ERICSSON,

      -- SDCCH Drop Rate - ERICSSON
      100.0 * COALESCE(SUM(CAST(CNDROP AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_ERICSSON,

      -- SDCCH Traffic - ERICSSON (Erlangs)
      COALESCE(SUM(CAST(CTRALACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CNSCAN AS DOUBLE)), 0), 0) AS SDCCH_TRAFFIC_ERICSSON,

      -- SDCCH Blocking Rate - ERICSSON (Vendor-specific)
      100.0 * COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0), 0) AS SDCCH_BLOCKING_RATE_ERICSSON,

      -- SDCCH Congestion Rate - ERICSSON
      100.0 * (COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) + COALESCE(SUM(CAST(CCONGSSUB AS DOUBLE)), 0)) /
        NULLIF(COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_ERICSSON,

      COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) TRAFFIC_DATA_GB_ERICSSON,
      COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) TRAFFIC_VOIX_ERICSSON,
      
       CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end downtime_sec
  
      

    FROM
      hourly_ericsson_arcep_2g_counters e
    -- LEFT JOIN
    --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

    WHERE
      e.DATE BETWEEN '2026-02-12' AND '2026-02-19'  -- Adjust date range as needed

    GROUP BY
      e.DATE,
       e.TIME,
       e.CELL_NAME
      -- ept.SITE_NAME,

      having  CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end > 1800
   
   -- HAVING  (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0)) < 4860
   
  -- DESC 
 ) t1
 LEFT JOIN
    EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

   

GROUP BY date ,time , ept.SITE_NAME
-- , cell_name 
 -- HAVING avg(downtime_sec) > 1800
)
t1


GROUP BY date , site_name 










########################################################333
##########################################################333
########################################################3
#################################################
###########here is like keep only cell doing more than 1800 and average their site

 select  distinct site_name 

FROM 
(
 select date  ,time, ept.SITE_NAME   , avg(downtime_sec) avg_down_per_site

  FROM 
 (
 SELECT
      e.DATE,
        e.TIME,
      e.CELL_NAME,
      -- ept.SITE_NAME,
      -- ept.ARRONDISSEMENT,
      -- ept.COMMUNE,
      -- ept.DEPARTEMENT,

      -- CSSR (Call Setup Success Rate) - ERICSSON
      CASE
        WHEN COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) = 0
          OR (COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
            ) = 0
        THEN 0
        ELSE
          100.0
          * (1.0 - (SUM(CAST(CCONGS AS DOUBLE))
                     / SUM(CAST(CCALLS AS DOUBLE))))
          * (1.0 - ((SUM(CAST(CNDROP AS DOUBLE))
                      - SUM(CAST(CNRELCONG AS DOUBLE)))
                     / SUM(CAST(CMSESTAB AS DOUBLE))))
          * (SUM(CAST(TCASSALL AS DOUBLE))
              / SUM(CAST(TASSALL AS DOUBLE)))
          * (1.0 - (
              (SUM(CAST(TFNDROP AS DOUBLE))
                + SUM(CAST(THNDROP AS DOUBLE))
                + SUM(CAST(TFNDROPSUB AS DOUBLE))
                + SUM(CAST(THNDROPSUB AS DOUBLE))
              )
              / (
                SUM(CAST(TFCASSALL AS DOUBLE))
                + SUM(CAST(THCASSALL AS DOUBLE))
                + SUM(CAST(TFCASSALLSUB AS DOUBLE))
                + SUM(CAST(THCASSALLSUB AS DOUBLE))
              )
            ))
      END AS CSSR_ERICSSON,

      -- 2G Cell Availability Rate - ERICSSON
      100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0), 0)) AS CELL_AVAILABILITY_RATE_ERICSSON,

      
       CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end downtime_sec
  
      

    FROM
      hourly_ericsson_arcep_2g_counters e
    -- LEFT JOIN
    --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

    WHERE
      e.DATE BETWEEN '2026-03-02' AND '2026-03-22'  -- Adjust date range as needed

    GROUP BY
      e.DATE,
       e.TIME,
       e.CELL_NAME
      -- ept.SITE_NAME,

      having  CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end > 1800
   
   -- HAVING  (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0)) < 4860
   
  -- DESC 
 ) t1
 LEFT JOIN
    EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

   

GROUP BY date ,time , ept.SITE_NAME
-- , cell_name 
 -- HAVING avg(downtime_sec) > 1800

) as t2










select date  ,time, ept.SITE_NAME   , avg(downtime_sec) avg_down_per_site

  FROM 
 (
 SELECT
      e.DATE,
        e.TIME,
      e.CELL_NAME,
      -- ept.SITE_NAME,
      -- ept.ARRONDISSEMENT,
      -- ept.COMMUNE,
      -- ept.DEPARTEMENT,

      -- CSSR (Call Setup Success Rate) - ERICSSON
      CASE
        WHEN COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) = 0
          OR (COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
            ) = 0
        THEN 0
        ELSE
          100.0
          * (1.0 - (SUM(CAST(CCONGS AS DOUBLE))
                     / SUM(CAST(CCALLS AS DOUBLE))))
          * (1.0 - ((SUM(CAST(CNDROP AS DOUBLE))
                      - SUM(CAST(CNRELCONG AS DOUBLE)))
                     / SUM(CAST(CMSESTAB AS DOUBLE))))
          * (SUM(CAST(TCASSALL AS DOUBLE))
              / SUM(CAST(TASSALL AS DOUBLE)))
          * (1.0 - (
              (SUM(CAST(TFNDROP AS DOUBLE))
                + SUM(CAST(THNDROP AS DOUBLE))
                + SUM(CAST(TFNDROPSUB AS DOUBLE))
                + SUM(CAST(THNDROPSUB AS DOUBLE))
              )
              / (
                SUM(CAST(TFCASSALL AS DOUBLE))
                + SUM(CAST(THCASSALL AS DOUBLE))
                + SUM(CAST(TFCASSALLSUB AS DOUBLE))
                + SUM(CAST(THCASSALLSUB AS DOUBLE))
              )
            ))
      END AS CSSR_ERICSSON,

      -- 2G Cell Availability Rate - ERICSSON
      100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0), 0)) AS CELL_AVAILABILITY_RATE_ERICSSON,

      
       CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end downtime_sec
  
      

    FROM
      hourly_ericsson_arcep_2g_counters e
    -- LEFT JOIN
    --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

    WHERE
      e.DATE BETWEEN '2026-03-02' AND '2026-03-08'  -- Adjust date range as needed




    GROUP BY
      e.DATE,
       e.TIME,
       e.CELL_NAME
      -- ept.SITE_NAME,

      having  CASE
  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
   THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
   ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) end > 1800
   
   -- HAVING  (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0)) < 4860
   
  -- DESC 
 ) t1
 LEFT JOIN
    EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'


GROUP BY date ,time , ept.SITE_NAME
-- , cell_name 
 -- HAVING avg(downtime_sec) > 1800


#############################
############################
############################



















########################################################333
##########################################################333
########################################################3
#################################################
###########here is like keep only cell doing more than 1800 and average their site

###HUAWEI





 select date  
 ,TIME
-- , t1.cell_name
 , ept.SITE_NAME   , avg(downtime_sec) avg_down_per_site
 -- ,sum(downtime_sec_manual)

  FROM (


    SELECT
      h.date,
      h.time,
      h.cell_name

      ,100 * (SUM(CELL_KPI_SD_SUCC
      ) / SUM(CELL_KPI_SD_REQ)) * 
  (1 - (SUM(CELL_SD_CALL_DROPS) / SUM(CELL_KPI_SD_SUCC))) * 
  (SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)) /
  (SUM(CELL_KPI_TCH_REQ_SIG) + SUM(CELL_KPI_TCH_ASS_REQ_TRAF) + SUM(CELL_KPI_TCH_HO_REQ_TRAF)) *
  (1 - (((sum(CELL_KPI_TCH_DROPS_SIG)+sum(CELL_KPI_TCH_STATIC_DROPS_TRAF)+sum(CELL_KPI_TCH_HO_DROPS_TRAF))) /
    ((sum(CELL_KPI_TCH_SUCC_SIG)+sum(CELL_KPI_TCH_ASS_SUCC_TRAF)+sum(CELL_KPI_TCH_HO_SUCC_TRAF))))) AS  CSSR_HUAWEI,

      -- 2G Availability Rate - HUAWEI
      100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0), 0) AS CELL_AVAILABILITY_RATE_HUAWEI,

      sum(CELL_SERV_OOS) downtime_sec,
      sum(`CELL_SERV_OOS_OM`) downtime_sec_manual

    FROM
      hourly_huawei_2g_all_counters h
    -- LEFT JOIN
    --   EPT_2G ept ON h.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'

    WHERE
      h.date BETWEEN '2026-03-02' AND '2026-03-08'  -- Adjust date range as needed

    GROUP BY
      h.date,
      h.time
      , h.CELL_NAME
      -- ept.SITE_NAME,
      -- ept.ARRONDISSEMENT,
      -- ept.COMMUNE,
      -- ept.DEPARTEMENT
      having  sum(CELL_SERV_OOS) > 1800
      and  sum(`CELL_SERV_OOS_OM`) = 0 

) t1
 LEFT JOIN
    EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'
GROUP BY date 
,TIME 
-- , t1.cell_name
, ept.SITE_NAME
-- , cell_name 
 -- HAVING avg(downtime_sec) > 1800


































