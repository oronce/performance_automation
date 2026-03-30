
-- Huawei 2G CSR Failure Component Breakdown (network level, no GROUP BY)
-- Returns one row: raw failure counts + % contribution of each component to total CSR failures
-- Formulas are identical to those in 2g_huawei_worst_cell.sql inner query

SELECT
    SDCCH_ASSIGN_FAILS,
    SDCCH_DROPS,
    TCH_ASSIGN_FAILS,
    TCH_DROPS,
    CSR_FAILURES,

    ROUND(100.0 * SDCCH_ASSIGN_FAILS / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_SDCCH_ASSIGN,
    ROUND(100.0 * SDCCH_DROPS        / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_SDCCH_DROPS,
    ROUND(100.0 * TCH_ASSIGN_FAILS   / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_TCH_ASSIGN,
    ROUND(100.0 * TCH_DROPS          / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_TCH_DROPS

FROM (
    SELECT
        SUM((CELL_KPI_SD_REQ - CELL_KPI_SD_SUCC) + CELL_SD_CALL_DROPS +
                   (CELL_KPI_TCH_REQ_SIG + CELL_KPI_TCH_ASS_REQ_TRAF + CELL_KPI_TCH_HO_REQ_TRAF) -
                   (CELL_KPI_TCH_SUCC_SIG + CELL_KPI_TCH_ASS_SUCC_TRAF + CELL_KPI_TCH_HO_SUCC_TRAF) +
                   (CELL_KPI_TCH_DROPS_SIG + CELL_KPI_TCH_STATIC_DROPS_TRAF + CELL_KPI_TCH_HO_DROPS_TRAF))  AS CSR_FAILURES,

        SUM(CELL_KPI_SD_REQ - CELL_KPI_SD_SUCC)                                                              AS SDCCH_ASSIGN_FAILS,

        SUM(CELL_SD_CALL_DROPS)                                                                               AS SDCCH_DROPS,

        SUM((CELL_KPI_TCH_REQ_SIG + CELL_KPI_TCH_ASS_REQ_TRAF + CELL_KPI_TCH_HO_REQ_TRAF) -
                   (CELL_KPI_TCH_SUCC_SIG + CELL_KPI_TCH_ASS_SUCC_TRAF + CELL_KPI_TCH_HO_SUCC_TRAF))        AS TCH_ASSIGN_FAILS,

        SUM((CELL_KPI_TCH_DROPS_SIG + CELL_KPI_TCH_STATIC_DROPS_TRAF + CELL_KPI_TCH_HO_DROPS_TRAF))         AS TCH_DROPS

    FROM hourly_huawei_2g_all_counters h
    WHERE h.date BETWEEN '{start_date}' AND '{end_date}'
    {time_filter}
) AS T