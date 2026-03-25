SELECT
            T1.date,
            T1.TIME,
            -- T1.cell_name,
            T1.`PS_DROP_HUAWEI`,

            T3.`CS_CSSR_HUAWEI`,
            T3.`CALL_BLOCK_RATE_HUAWEI`,
            T3.`CS_DROP`,

            T3.`PS_CSSR_HUAWEI`,
            T3.`DEBIT_DL_HUAWEI`,
            T3.`DEBIT_UL_HUAWEI`,

            T1.CELL_AVAILABILITY_HUAWEI,
            T1.Total_PS_Traffic_GB_HUAWEI,
           
            T2.`TRAFFIC_VOIX_HUAWEI`,
            T2.IRAT_HO_SUCCESS_RATE_HUAWEI,
            T2.HO_SUCCESS_RATE_HUAWEI
        FROM
            (
                -- T1: From hourly_huawei_3g_all_counters_1
                SELECT
                    date,
                    time,
                    -- cell_name,
                    CASE
                        WHEN (COALESCE(SUM(CAST(VS_RAB_NormRel_PS AS UNSIGNED)),0) + COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS AS UNSIGNED)),0) -
                              COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS_PCH AS UNSIGNED)),0) - COALESCE(SUM(CAST(VS_RAB_NormRel_PS_PCH AS UNSIGNED)),0) +
                              COALESCE(SUM(CAST(VS_DCCC_D2P_Succ AS UNSIGNED)),0) + COALESCE(SUM(CAST(VS_DCCC_Succ_F2P AS UNSIGNED)),0)) = 0
                        THEN NULL
                        ELSE ROUND((100 *
                            (COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS AS UNSIGNED)),0) - COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS_PCH AS UNSIGNED)),0) -
                             COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS_D2P AS UNSIGNED)),0) - COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS_F2P AS UNSIGNED)),0))
                        ) /
                        (
                            COALESCE(SUM(CAST(VS_RAB_NormRel_PS AS UNSIGNED)),0) + COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS AS UNSIGNED)),0) -
                            COALESCE(SUM(CAST(VS_RAB_AbnormRel_PS_PCH AS UNSIGNED)),0) - COALESCE(SUM(CAST(VS_RAB_NormRel_PS_PCH AS UNSIGNED)),0) +
                            COALESCE(SUM(CAST(VS_DCCC_D2P_Succ AS UNSIGNED)),0) + COALESCE(SUM(CAST(VS_DCCC_Succ_F2P AS UNSIGNED)),0)
                        ), 3)
                    END AS `PS_DROP_HUAWEI`,
                    100 * (
                        (SUM(CAST(RRC_SuccConnEstab_CallReEst AS UNSIGNED)) + SUM(CAST(RRC_SuccConnEstab_EmgCall AS UNSIGNED)) +
                         SUM(CAST(RRC_SuccConnEstab_OrgConvCall AS UNSIGNED)) + SUM(CAST(RRC_SuccConnEstab_OrgSubCall AS UNSIGNED)) +
                         SUM(CAST(RRC_SuccConnEstab_TmConvCall AS UNSIGNED)) + SUM(CAST(RRC_SuccConnEstab_Unkown AS UNSIGNED))) /
                        NULLIF((SUM(CAST(RRC_AttConnEstab_CallReEst AS UNSIGNED)) + SUM(CAST(RRC_AttConnEstab_EmgCall AS UNSIGNED)) +
                         SUM(CAST(RRC_AttConnEstab_OrgSubCall AS UNSIGNED)) + SUM(CAST(RRC_AttConnEstab_OrgConvCall AS UNSIGNED)) +
                         SUM(CAST(RRC_AttConnEstab_TmConvCall AS UNSIGNED)) + SUM(CAST(RRC_AttConnEstab_Unknown AS UNSIGNED))), 0)
                    ) * (
                        (SUM(CAST(VS_HSPA_RAB_SuccEstab_CS_Conv AS UNSIGNED)) + SUM(CAST(VS_RAB_SuccEstabCS_Conv AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_SuccEstabCS_Str AS UNSIGNED)) + SUM(CAST(VS_RAB_SuccEstabCS_AMR AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_SuccEstabCS_AMRWB AS UNSIGNED))) /
                        NULLIF((SUM(CAST(VS_HSPA_RAB_AttEstab_CS_Conv AS UNSIGNED)) + SUM(CAST(VS_RAB_AttEstabCS_Conv AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_AttEstabCS_Str AS UNSIGNED)) + SUM(CAST(VS_RAB_AttEstab_AMR AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_AttEstabCS_AMRWB AS UNSIGNED))), 0)
                    ) * (
                        1 - (SUM(CAST(VS_RAB_AbnormRel_AMR AS UNSIGNED)) + SUM(CAST(VS_RAB_AbnormRel_AMRWB AS UNSIGNED)) +
                             SUM(CAST(VS_RAB_AbnormRel_CS_HSPA_Conv AS UNSIGNED))) /
                        NULLIF((SUM(CAST(VS_RAB_AbnormRel_AMR AS UNSIGNED)) + SUM(CAST(VS_RAB_AbnormRel_AMRWB AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_AbnormRel_CS_HSPA_Conv AS UNSIGNED)) + SUM(CAST(VS_RAB_NormRel_CS AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_NormRel_CS_HSPA_Conv AS UNSIGNED)) + SUM(CAST(VS_RAB_NormRel_AMRWB AS UNSIGNED))), 0)
                    ) AS `CS_CSSR_HUAWEI`,
                    100 * (
                        (SUM(CAST(VS_RAB_FailEstabCS_DLIUBBand_Cong AS UNSIGNED)) + SUM(CAST(VS_RAB_FailEstabCS_ULIUBBand_Cong AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_FailEstabCS_ULCE_Cong AS UNSIGNED)) + SUM(CAST(VS_RAB_FailEstabCS_DLCE_Cong AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_FailEstabCS_Code_Cong AS UNSIGNED)) + SUM(CAST(VS_RAB_FailEstabCS_ULPower_Cong AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_FailEstabCS_DLPower_Cong AS UNSIGNED))) /
                        NULLIF((SUM(CAST(VS_RAB_AttEstabCS_Conv AS UNSIGNED)) + SUM(CAST(VS_RAB_AttEstabCS_Str AS UNSIGNED))), 0)
                    ) AS `CALL_BLOCK_RATE_HUAWEI`,
                    SUM(CAST(Total_PS_Traffic_GB AS UNSIGNED)) AS Total_PS_Traffic_GB_HUAWEI,
                    (1 - (SUM(CAST(VS_Cell_UnavailTime_Sys AS UNSIGNED))/(sum(60) * 60))) * 100 AS CELL_AVAILABILITY_HUAWEI

                FROM hourly_huawei_3g_all_counters_1 h1
                -- INNER JOIN EPT_3G  ON EPT_3G.`CELL_NAME` = h1.cell_name and `EPT_3G`.`VENDOR` = "HUAWEI"
                WHERE
                    h1.DATE BETWEEN '2026-02-01' AND  '2026-02-01'
                GROUP BY
                    h1.date, h1.time 
                    -- , cell_name
            ) AS T1
        INNER JOIN
            (
                -- T2: From hourly_huawei_3g_all_counters_2
                SELECT
                    date,
                    TIME,
                    -- cell_name,
                    100 * (
                        (SUM(CAST(RRC_SuccConnEstab_OrgInterCall AS double)) + SUM(CAST(RRC_SuccConnEstab_TmItrCall AS UNSIGNED)) +
                         SUM(CAST(RRC_SuccConnEstab_OrgBkgCall AS double)) + SUM(CAST(RRC_SuccConnEstab_TmBkgCall AS UNSIGNED)) +
                         SUM(CAST(RRC_SuccConnEstab_OrgSubCall AS double)) + SUM(CAST(RRC_SuccConnEstab_OrgStrCall AS UNSIGNED)) +
                         SUM(CAST(RRC_SuccConnEstab_TmStrCall AS double)) + SUM(CAST(VS_RRC_AttConnEstab_EDCH AS UNSIGNED)) +
                         SUM(CAST(VS_RRC_AttConnEstab_HSDSCH AS double))) /
                        NULLIF((SUM(CAST(RRC_AttConnEstab_OrgInterCall AS double)) + SUM(CAST(RRC_AttConnEstab_TmInterCall AS UNSIGNED)) +
                         SUM(CAST(RRC_AttConnEstab_TmBkgCall AS double)) + SUM(CAST(RRC_AttConnEstab_OrgBkgCall AS UNSIGNED)) +
                         SUM(CAST(RRC_AttConnEstab_OrgSubCall AS double)) + SUM(CAST(RRC_AttConnEstab_OrgStrCall AS UNSIGNED)) +
                         SUM(CAST(RRC_AttConnEstab_TmStrCall AS double)) + SUM(CAST(VS_RRC_SuccConnEstab_EDCH AS UNSIGNED)) +
                         SUM(CAST(VS_RRC_SuccConnEstab_HSDSCH AS double))), 0)
                    ) * (
                        (SUM(CAST(VS_RAB_SuccEstabPS_Conv AS double)) + SUM(CAST(VS_RAB_SuccEstabPS_Str AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_SuccEstabPS_Int AS double)) + SUM(CAST(VS_RAB_SuccEstabPS_Bkg AS UNSIGNED))) /
                        NULLIF((SUM(CAST(VS_RAB_AttEstabPS_Conv AS double)) + SUM(CAST(VS_RAB_AttEstabPS_Str AS UNSIGNED)) +
                         SUM(CAST(VS_RAB_AttEstabPS_Int AS double)) + SUM(CAST(VS_RAB_AttEstabPS_Bkg AS UNSIGNED))), 0)
                    ) AS `PS_CSSR_HUAWEI`,
                    AVG(CAST(VS_HSDPA_MeanChThroughput AS double)) AS `DEBIT_DL_HUAWEI`,
                    AVG(CAST(VS_HSUPA_MeanChThroughput AS double)) AS `DEBIT_UL_HUAWEI`,
                    SUM(CAST(VS_AMR_Erlang_BestCell AS double)) AS `TRAFFIC_VOIX_HUAWEI`,
                    100.0 * (SUM(CAST(VS_SHO_SuccRLAdd AS double))+SUM(CAST(VS_SHO_SuccRLDel AS UNSIGNED))) / NULLIF((SUM(CAST(VS_SHO_AttRLAdd AS UNSIGNED))+SUM(CAST(VS_SHO_AttRLDel AS UNSIGNED))),0) AS HO_SUCCESS_RATE_HUAWEI,
                    100.0 * SUM(CAST(IRATHO_SuccOutCS AS double)) / NULLIF(SUM(CAST(IRATHO_AttOutCS AS UNSIGNED)), 0) AS IRAT_HO_SUCCESS_RATE_HUAWEI                    

                FROM hourly_huawei_3g_all_counters_2 h2
                -- INNER JOIN EPT_3G ON EPT_3G.`CELL_NAME` = h2.cell_name and `EPT_3G`.`VENDOR` = "HUAWEI"
                WHERE
                    h2.DATE BETWEEN '2026-02-01' AND  '2026-02-01'
                GROUP BY
                    h2.date, H2.TIME 
                    -- , cell_name
            ) AS T2
        ON
            T1.date = T2.date and 
            T1.TIME = T2.TIME
            -- T1.cell_name = T2.cell_name
        INNER JOIN  (
            SELECT 
  DATE  
 ,time
 -- DATE_FORMAT(date, '%Y-%m') DATE
-- ,substring_index(substring_index(daily_arcep_huawei_3g.UCELL,'=',-3),',',1)
  -- ,NE_Name
  
  ,100 *
  (
    (
      SUM(CAST(NSRRCCallReest AS UNSIGNED)) +
      SUM(CAST(NSRRCCEmgCall AS UNSIGNED)) +
      SUM(CAST(OrgConvCall AS UNSIGNED)) +
      SUM(CAST(OrgSubCall AS UNSIGNED)) +
      SUM(CAST(TmConvCall AS UNSIGNED)) +
      SUM(CAST(Unknown AS UNSIGNED))
    )
    /
    NULLIF(
      SUM(CAST(AttCallReEst AS UNSIGNED)) +
      SUM(CAST(AttEmgCall AS UNSIGNED)) +
      SUM(CAST(AtOrgConvCall AS UNSIGNED)) +
      SUM(CAST(AtOrgSubCall AS UNSIGNED)) +
      SUM(CAST(AtTmConvCall AS UNSIGNED)) +
      SUM(CAST(AtUnknown AS UNSIGNED))
    , 0)
  )
  *
  (
    (
      SUM(CAST(SucHsCsConv AS UNSIGNED)) +
      SUM(CAST(SucRabEst AS UNSIGNED)) +
      SUM(CAST(SucCSStr AS UNSIGNED)) +
      SUM(CAST(SucAMR AS UNSIGNED)) +
      SUM(CAST(SucAMRWB AS UNSIGNED))
    )
    /
    NULLIF(
      SUM(CAST(AttHsCsConv AS UNSIGNED)) +
      SUM(CAST(CSConvRabEstReq AS UNSIGNED)) +
      SUM(CAST(CSStrRabEstReq AS UNSIGNED)) +
      SUM(CAST(AttAMR AS UNSIGNED)) +
      SUM(CAST(AttAMRWB AS UNSIGNED))
    , 0)
  )
  *
  (
    1 -
    (
      (SUM(CAST(NCsAbnAMR AS UNSIGNED)) +
       SUM(CAST(AtAbnAMRWB AS UNSIGNED)) +
       SUM(CAST(AtCsAbnHS AS UNSIGNED))
      )
      /
      NULLIF(
        SUM(CAST(NCsRabNor AS UNSIGNED)) +
        SUM(CAST(NCsAbnAMR AS UNSIGNED)) +
        (
          SUM(CAST(AtAbnAMRWB AS UNSIGNED)) +
          SUM(CAST(AtCsAbnHS AS UNSIGNED)) +
          SUM(CAST(AtCsNorHS AS UNSIGNED)) +
          SUM(CAST(AtNorAMRWB AS UNSIGNED))
        )
      , 0)
    )
  ) AS CS_CSSR_HUAWEI,
  100 *
  (
    (SUM(CAST(AtAbnAMRWB AS UNSIGNED)) + SUM(CAST(AtCsAbnHS AS UNSIGNED)))
    /
    NULLIF(
      (SUM(CAST(SucHsCsConv AS UNSIGNED)) + SUM(CAST(SucAMR AS UNSIGNED)) + SUM(CAST(SucAMRWB AS UNSIGNED))
      ), 0)
  ) AS CS_DROP ,
  100 *
  (
    (
      SUM(CAST(FailRabEstDlIub AS UNSIGNED)) 
      + SUM(CAST(FailRabestUlIub AS UNSIGNED)) 
      + SUM(CAST(FailRabEstUlCECong AS UNSIGNED)) 
      + SUM(CAST(FailRabEstDlCECong AS UNSIGNED)) 
      + SUM(CAST(FailRabEstCodeCong AS UNSIGNED)) 
      + SUM(CAST(FailRabEstUlPwrCong AS UNSIGNED)) 
      + SUM(CAST(FailRabEstDlPwrCong AS UNSIGNED))
    )
    /
    NULLIF(
      (SUM(CAST(CSConvRabEstReq AS UNSIGNED)) + SUM(CAST(CSStrRabEstReq AS UNSIGNED))
      ), 0)
  ) as CALL_BLOCK_RATE_HUAWEI,
 100 *
  (
    (
      (SUM(CAST(OrgInterCall AS UNSIGNED)) 
       + SUM(CAST(TmItrCall AS UNSIGNED)) 
       + SUM(CAST(OrgBkgCall AS UNSIGNED)) 
       + SUM(CAST(TmBkgCall AS UNSIGNED)) 
       + SUM(CAST(TmStrCall AS UNSIGNED)) 
       + SUM(CAST(OrgStrCall AS UNSIGNED)) 
       + SUM(CAST(OrgSubCall AS UNSIGNED)) 
       + SUM(CAST(AttHSDSCH AS UNSIGNED)) 
       + SUM(CAST(AttEDCH AS UNSIGNED))
      )
      /
      NULLIF(
        (SUM(CAST(AttOrgItrCall AS UNSIGNED)) 
         + SUM(CAST(AttTmItrCall AS UNSIGNED)) 
         + SUM(CAST(AttOrgBkgCall AS UNSIGNED)) 
         + SUM(CAST(AttTmBkgCall AS UNSIGNED)) 
         + SUM(CAST(AttOrgStrCall AS UNSIGNED)) 
         + SUM(CAST(AttTmStrCall AS UNSIGNED)) 
         + SUM(CAST(AtOrgSubCall AS UNSIGNED)) 
         + SUM(CAST(SuccEDCH AS UNSIGNED)) 
         + SUM(CAST(SuccHSDSCH AS UNSIGNED))
        ), 0)
    )
    *
    (
      (SUM(CAST(SucRabPSConv AS UNSIGNED)) 
       + SUM(CAST(SucRabPSStr AS UNSIGNED)) 
       + SUM(CAST(SucRabPSInter AS UNSIGNED)) 
       + SUM(CAST(SucRabPSBkg AS UNSIGNED)))
      /
      NULLIF(
        (SUM(CAST(AttRabPSConv AS UNSIGNED)) 
         + SUM(CAST(AttRabPSStr AS UNSIGNED)) 
         + SUM(CAST(AttRabPSInter AS UNSIGNED)) 
         + SUM(CAST(AttRabPSBkg AS UNSIGNED))
        ), 0)
    )
  ) AS PS_CSSR_HUAWEI,
  100 *
  (
    (SUM(CAST(AbnPSRabPCH AS UNSIGNED)) - SUM(CAST(AbnPSRabD2P AS UNSIGNED)) - SUM(CAST(CDRF2P AS UNSIGNED)))
    /
    NULLIF(
      (SUM(CAST(AbnPSRabPCH AS UNSIGNED)) - SUM(CAST(NormPSRabPCH AS UNSIGNED)) 
       + SUM(CAST(SuccD2P AS UNSIGNED)) + SUM(CAST(SuccFach AS UNSIGNED))
      ), 0)
  ) AS PS_DROP_HUAWEI,
      avg(CAST(DLHSTput AS DECIMAL)) AS DEBIT_DL_HUAWEI,
    avg(CAST(ULHSTput AS DECIMAL)) AS DEBIT_UL_HUAWEI
  --  round(AVG(CAST(NULLIF(DLHSTput,'') AS DECIMAL(10,2))),4) AS DLHSTput_v,

   --  round(AVG(CAST(NULLIF(ULHSTput,'') AS DECIMAL(10,2))),3) AS ULHSTput_v
FROM hourly_arcep_huawei_3g 
WHERE DATE between   '2026-02-01' AND  '2026-02-01'
-- AND NE_Name='PKMBSC03'

 -- AND substring_index(substring_index(daily_arcep_huawei_3g.UCELL,'=',-3),',',1) NOT IN 
--  (
--  select cellule  from weekly_huawei_3g_disponibilite
--         WHERE DATE='2025-06-15' AND ( availibility_3g=0 OR availibility_3g='')
--  )
-- group by DATE_FORMAT(date, '%Y-%m')


   GROUP BY DATE , TIME
) AS T3
        ON
            T1.date = T3.date and 
            T1.TIME = T3.TIME