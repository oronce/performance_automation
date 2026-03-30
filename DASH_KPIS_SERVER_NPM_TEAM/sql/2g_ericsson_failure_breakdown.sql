
-- Ericsson 2G CSR Failure Component Breakdown (network level, no GROUP BY)
-- Returns one row: raw failure counts + % contribution of each component to total CSR failures
-- Formulas are identical to those in 2g_ericsson_worst_cell.sql inner query

SELECT
    NUMBER_SDCONG,
    NUMBER_OF_SDDROPS,
    TCH_ASSIGN_FAILS,
    NUMBER_OF_TCH_DROPS,
    CSR_FAILURES,

    ROUND(100.0 * NUMBER_SDCONG       / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_SDCONG,
    ROUND(100.0 * NUMBER_OF_SDDROPS   / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_SDDROPS,
    ROUND(100.0 * TCH_ASSIGN_FAILS    / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_TCH_ASSIGN,
    ROUND(100.0 * NUMBER_OF_TCH_DROPS / NULLIF(CSR_FAILURES, 0), 2)  AS WEIGHT_TCH_DROPS

FROM (
    SELECT
        SUM(CCONGS)                                                                        AS NUMBER_SDCONG,
        SUM(CNDROP) - SUM(CNRELCONG)                                                       AS NUMBER_OF_SDDROPS,
        SUM(TASSALL) - SUM(TCASSALL)                                                       AS TCH_ASSIGN_FAILS,
        SUM(TFNDROP) + SUM(THNDROP) + SUM(TFNDROPSUB) + SUM(THNDROPSUB)                   AS NUMBER_OF_TCH_DROPS,
        SUM(CCONGS) + (SUM(CNDROP) - SUM(CNRELCONG)) + (SUM(TASSALL) - SUM(TCASSALL)) +
        (SUM(TFNDROP) + SUM(THNDROP) + SUM(TFNDROPSUB) + SUM(THNDROPSUB))                 AS CSR_FAILURES

    FROM hourly_ericsson_arcep_2g_counters e
    WHERE e.DATE BETWEEN '{start_date}' AND '{end_date}'
    {time_filter}
) AS T