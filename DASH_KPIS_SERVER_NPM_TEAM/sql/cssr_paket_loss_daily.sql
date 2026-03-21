

WITH
  HUAWEI_2G_KPI AS (
    SELECT
      h.date,
      100 * (SUM(CELL_KPI_SD_SUCC) / SUM(CELL_KPI_SD_REQ)) *
        (1 - (SUM(CELL_SD_CALL_DROPS) / SUM(CELL_KPI_SD_SUCC))) *
        (SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)) /
        (SUM(CELL_KPI_TCH_REQ_SIG) + SUM(CELL_KPI_TCH_ASS_REQ_TRAF) + SUM(CELL_KPI_TCH_HO_REQ_TRAF)) *
        (1 - (((SUM(CELL_KPI_TCH_DROPS_SIG) + SUM(CELL_KPI_TCH_STATIC_DROPS_TRAF) + SUM(CELL_KPI_TCH_HO_DROPS_TRAF)))
            / ((SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)))))
      AS CSSR_HUAWEI
    FROM hourly_huawei_2g_all_counters h
    WHERE h.date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY h.date
  ),

  ERICSSON_2G_KPI AS (
    SELECT
      e.DATE,
      CASE
        WHEN COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) = 0
          OR COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) = 0
          OR (COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
               + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)) = 0
        THEN 0
        ELSE
          100.0
          * (1.0 - (SUM(CAST(CCONGS AS DOUBLE)) / SUM(CAST(CCALLS AS DOUBLE))))
          * (1.0 - ((SUM(CAST(CNDROP AS DOUBLE)) - SUM(CAST(CNRELCONG AS DOUBLE))) / SUM(CAST(CMSESTAB AS DOUBLE))))
          * (SUM(CAST(TCASSALL AS DOUBLE)) / SUM(CAST(TASSALL AS DOUBLE)))
          * (1.0 - (
              (SUM(CAST(TFNDROP AS DOUBLE)) + SUM(CAST(THNDROP AS DOUBLE))
                + SUM(CAST(TFNDROPSUB AS DOUBLE)) + SUM(CAST(THNDROPSUB AS DOUBLE)))
              / (SUM(CAST(TFCASSALL AS DOUBLE)) + SUM(CAST(THCASSALL AS DOUBLE))
                + SUM(CAST(TFCASSALLSUB AS DOUBLE)) + SUM(CAST(THCASSALLSUB AS DOUBLE)))
            ))
      END AS CSSR_ERICSSON
    FROM hourly_ericsson_arcep_2g_counters e
    WHERE e.DATE BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY e.DATE
  ),

  ERICSSON_PACKET_LOSS AS (
    SELECT
        DATE,
        SUM(CAST(sctpAssocRtxChunks AS DOUBLE)) AS packet_loss_count_ericsson,
        100.0 * SUM(CAST(sctpAssocRtxChunks AS DOUBLE))
            / NULLIF(SUM(CAST(sctpAssocOutDataChunks AS DOUBLE)) + SUM(CAST(sctpAssocRtxChunks AS DOUBLE)), 0)
            AS packet_loss_pct_ericsson
    FROM hourly_ericsson_packet_loss_bb_4g_counters
    WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY DATE
  ),

  HUAWEI_PACKET_LOSS AS (
    SELECT
        DATE,
        SUM(CAST(h.VS_IPPOOL_IPPM_Local_TxPkts AS DECIMAL)) - SUM(CAST(h.VS_IPPOOL_IPPM_Peer_RxPkts AS DECIMAL)) AS packet_loss_count_huawei,
        ((SUM(CAST(h.VS_IPPOOL_IPPM_Local_TxPkts AS DECIMAL)) - SUM(CAST(h.VS_IPPOOL_IPPM_Peer_RxPkts AS DECIMAL)))
            / NULLIF(SUM(CAST(h.VS_IPPOOL_IPPM_Local_TxPkts AS DECIMAL)), 0)) * 100 AS packet_loss_pct_huawei
    FROM hourly_huawei_3g_packet_loss h
    LEFT JOIN huawei_adjacent_node_id_3g ha
        ON h.adjacent_node_id = ha.adjacent_node_id
        AND h.controller_name = ha.rnc
    WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY DATE
  )

SELECT
    COALESCE(h2g.date, e2g.DATE, epl.DATE, hpl.DATE)   AS DATE,

    -- CSSR
    h2g.CSSR_HUAWEI,
    e2g.CSSR_ERICSSON,
    (COALESCE(h2g.CSSR_HUAWEI, 0) * 0.22) + (COALESCE(e2g.CSSR_ERICSSON, 0) * 0.78) AS CSSR_NETWORK,

    -- Packet Loss
    epl.packet_loss_count_ericsson,
    epl.packet_loss_pct_ericsson,
    hpl.packet_loss_count_huawei,
    hpl.packet_loss_pct_huawei,
    COALESCE(epl.packet_loss_count_ericsson, 0) + COALESCE(hpl.packet_loss_count_huawei, 0) AS packet_loss_count_total

FROM HUAWEI_2G_KPI h2g
LEFT JOIN ERICSSON_2G_KPI     e2g ON h2g.date = e2g.DATE
LEFT JOIN ERICSSON_PACKET_LOSS epl ON COALESCE(h2g.date, e2g.DATE) = epl.DATE
LEFT JOIN HUAWEI_PACKET_LOSS   hpl ON COALESCE(h2g.date, e2g.DATE) = hpl.DATE

ORDER BY DATE
