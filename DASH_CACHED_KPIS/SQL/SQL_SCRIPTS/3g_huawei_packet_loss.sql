SELECT
    {select_fields},
    ((SUM(CAST(h.VS_IPPOOL_IPPM_Local_TxPkts AS DECIMAL)) - SUM(CAST(h.VS_IPPOOL_IPPM_Peer_RxPkts AS DECIMAL))) 
     / NULLIF(SUM(CAST(h.VS_IPPOOL_IPPM_Local_TxPkts AS DECIMAL)), 0)) * 100 AS packet_loss_pct
FROM hourly_huawei_3g_packet_loss h
LEFT JOIN huawei_adjacent_node_id_3g ha
    ON h.adjacent_node_id = ha.adjacent_node_id 
    AND h.controller_name = ha.rnc
LEFT JOIN (
    SELECT DISTINCT SITE_NAME, commune, arrondissement
    FROM ept_4g
    WHERE VENDOR = 'HUAWEI'
) e ON e.SITE_NAME = ha.site_name
WHERE {where_clause}
GROUP BY {group_by}




