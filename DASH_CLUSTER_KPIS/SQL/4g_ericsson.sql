SELECT
  DATE,
  TIME,

  -- PS_CSSR: LTE ERAB Setup Success Rate (%)
  100.0 * (
    COALESCE(SUM(CAST(pmRrcConnEstabSucc AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmRrcConnEstabAtt AS DOUBLE)), 0), 0)
  ) * (
    COALESCE(SUM(CAST(pmS1SigConnEstabSucc AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmS1SigConnEstabAtt AS DOUBLE)), 0), 0)
  ) * (
    COALESCE(SUM(CAST(pmErabEstabSuccInit AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmErabEstabAttInit AS DOUBLE)), 0), 0)
  ) AS PS_CSSR,

  -- ERAB_DROP: ERAB Drop Rate (%)
  100.0 * (
    COALESCE(SUM(CAST(pmErabRelAbnormalEnbAct AS DOUBLE)), 0) +
    COALESCE(SUM(CAST(pmErabRelMmeAct AS DOUBLE)), 0)
  ) / NULLIF(
    COALESCE(SUM(CAST(pmErabEstabSuccInit AS DOUBLE)), 0) +
    COALESCE(SUM(CAST(pmErabEstabSuccAdded AS DOUBLE)), 0), 0
  ) AS ERAB_DROP,

  -- DEBIT_DL: DL Cell Throughput (kbps)
  COALESCE(SUM(CAST(pmPdcpVolDlDrb AS DOUBLE)), 0) /
  NULLIF(COALESCE(SUM(CAST(pmSchedActivityCellDl AS DOUBLE)), 0), 0) AS DEBIT_DL,

  -- DEBIT_UL: UL Cell Throughput (kbps)
  COALESCE(SUM(CAST(pmPdcpVolUlDrb AS DOUBLE)), 0) /
  NULLIF(COALESCE(SUM(CAST(pmSchedActivityCellUl AS DOUBLE)), 0), 0) AS DEBIT_UL,

  -- DL_USER_THP: DL User Throughput (kbps)
  (
    COALESCE(SUM(CAST(pmPdcpVolDlDrb AS DOUBLE)), 0) -
    COALESCE(SUM(CAST(pmPdcpVolDlDrbLastTTI AS DOUBLE)), 0)
  ) / NULLIF(COALESCE(SUM(CAST(pmUeThpTimeDl AS DOUBLE)), 0), 0) AS DL_USER_THP,


    COALESCE(SUM(CAST(pmUeThpVolUl AS DOUBLE)), 0) /
  NULLIF(COALESCE(SUM(CAST(pmUeThpTimeUl AS DOUBLE)), 0) , 0) AS UL_USER_THP,

  -- INTRA_HOSR: Intra-frequency Handover Success Rate (%)
  100.0 * (
    COALESCE(SUM(CAST(pmHoPrepSuccLteIntraF AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmHoPrepAttLteIntraF AS DOUBLE)), 0), 0)
  ) * (
    COALESCE(SUM(CAST(pmHoExeSuccLteIntraF AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmHoExeAttLteIntraF AS DOUBLE)), 0), 0)
  ) AS INTRA_HOSR,

  -- INTER_HOSR: Inter-frequency Handover Success Rate (%)
  100.0 * (
    COALESCE(SUM(CAST(pmHoPrepSuccLteInterF AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmHoPrepAttLteInterF AS DOUBLE)), 0), 0)
  ) * (
    COALESCE(SUM(CAST(pmHoExeSuccLteInterF AS DOUBLE)), 0) /
    NULLIF(COALESCE(SUM(CAST(pmHoExeAttLteInterF AS DOUBLE)), 0), 0)
  ) AS INTER_HOSR,

  -- PRB_UTILIZATION: Physical Resource Block Utilization (%)
  100.0 * (
    (
      COALESCE(SUM(CAST(pmPrbUsedDlDtch AS DOUBLE)), 0) +
      COALESCE(SUM(CAST(pmPrbUsedDlBcch AS DOUBLE)), 0) +
      COALESCE(SUM(CAST(pmPrbUsedDlPcch AS DOUBLE)), 0) +
      COALESCE(SUM(CAST(pmPrbUsedDlSrbFirstTrans AS DOUBLE)), 0)
    ) * (
      1 + (
        COALESCE(SUM(CAST(pmPrbUsedDlReTrans AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(pmPrbUsedDlFirstTrans AS DOUBLE)), 0), 0)
      )
    )
  ) / NULLIF(COALESCE(SUM(CAST(pmPrbAvailDl AS DOUBLE)), 0), 0) AS PRB_UTILIZATION,

  100.0 * (
    (
        COALESCE(SUM(CAST(pmPrbUsedDlDtch AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(pmPrbUsedDlBcch AS DOUBLE)), 0) +
        COALESCE(SUM(CAST(pmPrbUsedDlPcch AS DOUBLE)), 0)
    ) 
    + 
    COALESCE(SUM(CAST(pmPrbUsedDlSrbFirstTrans AS DOUBLE)), 0) * (
        1 + COALESCE(SUM(CAST(pmPrbUsedDlReTrans AS DOUBLE)), 0) /
            NULLIF(COALESCE(SUM(CAST(pmPrbUsedDlFirstTrans AS DOUBLE)), 0), 0)
    )
) / NULLIF(COALESCE(SUM(CAST(pmPrbAvailDl AS DOUBLE)), 0) / 100, 0) / 100 AS PRB_UTILIZATION_DL_NEW,


  -- CELL_AVAILABILITY: Cell Availability (%)
  100.0 - (
    100.0 * (
      COALESCE(SUM(CAST(pmCellDowntimeAuto AS DOUBLE)), 0) +
      COALESCE(SUM(CAST(pmCellDowntimeMan AS DOUBLE)), 0)
    ) / NULLIF(COALESCE(SUM(CAST(PERIOD_DURATION AS UNSIGNED)), 0) * 60, 0)
  ) AS CELL_AVAILABILITY_WITH_MANUAL,

  100.0 * (
  (COALESCE(SUM(CAST(PERIOD_DURATION AS DOUBLE)), 0) * 60 
   - COALESCE(SUM(CAST(pmCellDowntimeAuto AS DOUBLE)), 0))
  / NULLIF(COALESCE(SUM(CAST(PERIOD_DURATION AS DOUBLE)), 0) * 60, 0)
) AS CELL_AVAILABILITY,

  -- CSFB_SR: Circuit-Switched Fallback Success Rate (%)
  100.0 * (
    COALESCE(SUM(CAST(pmUeCtxtRelCsfbWcdma AS DOUBLE)), 0) +
    COALESCE(SUM(CAST(pmUeCtxtRelCsfbGsm AS DOUBLE)), 0)
  ) / NULLIF(
    COALESCE(SUM(CAST(pmUeCtxtEstabAttCsfb AS DOUBLE)), 0) +
    COALESCE(SUM(CAST(pmUeCtxtModAttCsfb AS DOUBLE)), 0), 0
  ) AS CSFB_SR,

  -- LTE_ERAB_FAILURE: ERAB Establishment Failures (count)
  (
    COALESCE(SUM(CAST(pmErabEstabAttInit AS DOUBLE)), 0) +
    COALESCE(SUM(CAST(pmErabEstabAttAdded AS DOUBLE)), 0)
  ) - (
    COALESCE(SUM(CAST(pmErabEstabSuccInit AS DOUBLE)), 0) +
    COALESCE(SUM(CAST(pmErabEstabSuccAdded AS DOUBLE)), 0)
  ) AS LTE_ERAB_FAILURE,

  -- USER_CONNECTED: Maximum RRC Connected Users
  -- COALESCE(SUM(CAST(pmRrcConnMax AS DOUBLE)), 0) AS USER_CONNECTED,

  COALESCE(SUM(CAST(pmActiveUeDlSum AS DOUBLE)), 0) / COALESCE(SUM(CAST(pmSchedActivityCellDl AS DOUBLE)), 0) active_user

  COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) AS TRAFFIC_DATA_GB


FROM hourly_ericsson_arcep_4g_counters H

-- LEFT JOIN EPT_4G 
-- ON H.`CELL_NAME` = `EPT_4G`.`CELL_NAME`
-- AND `EPT_4G`.`VENDOR` = 'ERICSSON'

WHERE DATE BETWEEN '2026-03-15' AND '2026-03-15' 

GROUP BY DATE, TIME