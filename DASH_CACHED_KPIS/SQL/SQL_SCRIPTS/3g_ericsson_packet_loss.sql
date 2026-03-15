

 SELECT
                   {select_fields},


                        100.0 * SUM(CAST(sctpAssocRtxChunks AS DOUBLE))
                            / NULLIF(SUM(CAST(sctpAssocOutDataChunks AS DOUBLE)) + SUM(CAST(sctpAssocRtxChunks AS DOUBLE)), 0)
                            AS packet_loss_3g_bb 
                        FROM hourly_ericsson_packet_loss_bb_3g_counters e
                        LEFT JOIN
                                EPT_3G ept ON e.site_name = ept.site_name AND ept.VENDOR = 'ERICSSON'
                                WHERE {where_clause}
                        GROUP BY {group_by}








