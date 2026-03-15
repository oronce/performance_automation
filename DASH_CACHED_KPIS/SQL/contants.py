
QUERY_CONFIG = {

        "2G": {
            

            "HUAWEI": {
                
                
                "MAIN_KPIS": {
                    "query_type": "raw_sql",
                    "description": "2G Network KPIs HUAWEI ",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                

                        "huawei": {
                            "date_col": "h.date",
                            "time_col": "h.time",
                            "aggregations": {
                                "cell_name": "e.CELL_NAME",
                                "site_name": "e.SITE_NAME",
                                "commune": "e.COMMUNE"
                            }
                        },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "ept2g",
                            #"include_date": True,       # Always include date
                            #"include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                
                        SELECT
                            {huawei__select_fields}
                            -- h.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT,

                            
                            -- CASE
                            --   WHEN COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) = 0
                            --     OR COALESCE(SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)), 0) = 0
                            --     OR (COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)) = 0
                            --     OR (COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)) = 0
                            --   THEN 0
                            --   ELSE
                            --     100.0
                            --     * (SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))
                            --         / SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)))
                            --     * (1.0 - (SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE))
                            --                / SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))))
                            --     * ((SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                            --          + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                            --          + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))
                            --         / (SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE))
                            --             + SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE))
                            --             + SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE))))
                            --     * (1.0 - ((SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE))
                            --                 + SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE))
                            --                 + SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)))
                            --                / (SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                            --                    + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                            --                    + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))))
                            -- END AS CSSR_HUAWEI
                            

                            ,100 * (SUM(CELL_KPI_SD_SUCC
                            ) / SUM(CELL_KPI_SD_REQ)) * 
                        (1 - (SUM(CELL_SD_CALL_DROPS) / SUM(CELL_KPI_SD_SUCC))) * 
                        (SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)) /
                        (SUM(CELL_KPI_TCH_REQ_SIG) + SUM(CELL_KPI_TCH_ASS_REQ_TRAF) + SUM(CELL_KPI_TCH_HO_REQ_TRAF)) *
                        (1 - (((sum(CELL_KPI_TCH_DROPS_SIG)+sum(CELL_KPI_TCH_STATIC_DROPS_TRAF)+sum(CELL_KPI_TCH_HO_DROPS_TRAF))) /
                            ((sum(CELL_KPI_TCH_SUCC_SIG)+sum(CELL_KPI_TCH_ASS_SUCC_TRAF)+sum(CELL_KPI_TCH_HO_SUCC_TRAF))))) AS  CSSR_HUAWEI,

                            -- ARCEP 2G CALL DROP RATE - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0),
                                0
                            ) AS CDR_HUAWEI,

                            -- ARCEP 2G CALL BLOCKING RATE - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_CONG_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS CBR_HUAWEI,

                            -- TCH Congestion Rate - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS TCH_CONGESTION_RATE_HUAWEI,

                            -- SDCCH Congestion Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_KPI_SD_CONGEST AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_HUAWEI,

                            -- SDCCH Drop Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_IMM_ASS_SUCC_SD AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_HUAWEI,

                            -- ARCEP TCH Assignment Success Rate - HUAWEI (Vendor-specific)
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,

                            -- SDCCH Traffic (Erlangs) - HUAWEI
                            COALESCE(SUM(CAST(CELL_KPI_SD_TRAF_ERL AS DOUBLE)), 0) AS SDCCH_TRAFFIC_HUAWEI,

                            -- 2G Availability Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0), 0) AS CELL_AVAILABILITY_RATE_HUAWEI,


                                COALESCE(SUM(CAST(CELL_KPI_TCH_TRAF_ERL_TRAF AS DOUBLE)), 0) TRAFFIC_VOIX_HUAWEI,
                                -- handover sr
                                100.0 * (
                        (COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_SUCC AS DOUBLE)), 0)
                        + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_SUCC AS DOUBLE)), 0))
                        / NULLIF(
                            COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_CMD AS DOUBLE)), 0)
                            + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_CMD AS DOUBLE)), 0),
                            0
                            )
                        ) AS HANDOVER_SUCCESS_RATE_HUAWEI



                            FROM
                            hourly_huawei_2g_all_counters h
                            -- LEFT JOIN
                            --   EPT_2G ept ON h.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'

                            WHERE
                            {huawei__where_clause}

                            GROUP BY
                        {huawei__group_by}
                            -- h.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT

                            
                    """
                }
                

            }

            ,


            "ERICSSON": {
                
                
                "MAIN_KPIS": {
                    "query_type": "raw_sql",
                    "description": "2G Network KPIs HUAWEI ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "time_col": "e.TIME",
                            "aggregations": {
                                #"cell_name": "e.CELL_NAME",
                                "SITE_NAME": "ePT",
                                "COMMUNE": "ePT.COMMUNE",
                                "ARRONDISSEMENT": "ePT.ARRONDISSEMENT"
                            }
                        },
                        # "ept2g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "cell_name": "e.CELL_NAME",
                        #         "site_name": "e.SITE_NAME",
                        #         "commune": "e.COMMUNE"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "ept2g",
                            #"include_date": True,       # Always include date
                            #"include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                

                    SELECT
                    {eric__select_fields}
                    -- e.CELL_NAME,
                    -- ept.SITE_NAME,
                    -- ept.ARRONDISSEMENT,
                    -- ept.COMMUNE,
                    -- ept.DEPARTEMENT,

                    -- CSSR (Call Setup Success Rate) - ERICSSON
                    ,CASE
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
                    COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) TRAFFIC_VOIX_ERICSSON
                -- ,CASE
                --  WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
                --  THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
                --  ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE)) 
                -- END downtime_sec
                    FROM
                    hourly_ericsson_arcep_2g_counters e
                    LEFT JOIN
                    EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

                    WHERE
                    {eric__where_clause}

                    GROUP BY
                {eric__group_by}
                    -- e.CELL_NAME,
                    -- ept.SITE_NAME,
                    -- ept.ARRONDISSEMENT,
                    -- ept.COMMUNE,
                    -- ept.DEPARTEMENT

                    """
                }
                

            }

            ,

            
            "COMBINED": {

                "NETWORK": {
                    "query_type": "raw_sql",
                    "description": "2G Network KPIs HUAWEI ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "time_col": "e.TIME",
                            "aggregations": {
                            }
                        },
                        "huawei": {
                            "date_col": "h.date",
                            "time_col": "h.time",
                            "aggregations": {
                            }
                        },
                        "combined":{
                            "date_col": "COALESCE(h.date, e.DATE)",
                            "time_col": "COALESCE(h.time, e.TIME)",
                            "aggregations": {
                            }
                        }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "huawei",
                            "include_date": True,       # Always include date
                            "include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "chart_configs": {
                        "CSSR_ALL": {
                            "KPIS": ["CSSR_NETWORK", "CSSR_HUAWEI", "CSSR_ERICSSON"],
                            "title": "2G CSSR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CSSR (%)",
                            "threshold": 99
                        },
                        "CDR_ALL": {
                            "KPIS": ["CDR_NETWORK", "CDR_HUAWEI", "CDR_ERICSSON"],
                            "title": "2G CDR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CDR (%)"
                        },
                        "CBR_ALL": {
                            "KPIS": ["CBR_NETWORK", "CBR_HUAWEI", "CBR_ERICSSON"],
                            "title": "2G CBR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CBR (%)",
                            "threshold": 3
                        },
                        "TCH_CONGESTION_RATE_ALL": {
                            "KPIS": ["TCH_CONGESTION_RATE_NETWORK", "TCH_CONGESTION_RATE_HUAWEI", "TCH_CONGESTION_RATE_ERICSSON"],
                            "title": "2G TCH Congestion - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "TCH Congestion (%)",
                            "threshold": 2
                        },
                        "SDCCH_CONGESTION_RATE_ALL": {
                            "KPIS": ["SDCCH_CONGESTION_RATE_NETWORK", "SDCCH_CONGESTION_RATE_HUAWEI", "SDCCH_CONGESTION_RATE_ERICSSON"],
                            "title": "2G SDCCH Congestion - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Congestion (%)",
                            "threshold": 1
                        },
                        "SDCCH_DROP_RATE_ALL": {
                            "KPIS": ["SDCCH_DROP_RATE_NETWORK", "SDCCH_DROP_RATE_HUAWEI", "SDCCH_DROP_RATE_ERICSSON"],
                            "title": "2G SDCCH Drop Rate - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Drop Rate (%)"
                        },
                        "CELL_AVAILABILITY_ALL": {
                            "KPIS": ["CELL_AVAILABILITY_RATE_NETWORK", "CELL_AVAILABILITY_RATE_HUAWEI", "CELL_AVAILABILITY_RATE_ERICSSON"],
                            "title": "2G Cell Availability - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "Availability (%)",
                            "threshold": 99
                        },
                        "SDCCH_TRAFFIC_ALL": {
                            "KPIS": ["SDCCH_TRAFFIC_NETWORK", "SDCCH_TRAFFIC_HUAWEI", "SDCCH_TRAFFIC_ERICSSON"],
                            "title": "2G SDCCH Traffic - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Traffic (Erl)"
                        },

                        "CSSR_NETWORK_vs_CDR": {
                            "KPIS": ["CSSR_NETWORK", "CDR_NETWORK"],
                            "title": "2G Network CSSR vs CDR",
                            "default_type_1": "line",
                            "default_type_2": "bar",
                            "is_dual_axis": True,
                            "y_axis_titles": ["CSSR (%)", "CDR (%)"]
                        }

                    },

                    "sql_template": """
                        WITH
                        HUAWEI_2G_KPI AS (
                            SELECT
                            {huawei__select_fields}
                            -- h.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT,

                            
                            -- CASE
                            --   WHEN COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) = 0
                            --     OR COALESCE(SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)), 0) = 0
                            --     OR (COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)) = 0
                            --     OR (COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)) = 0
                            --   THEN 0
                            --   ELSE
                            --     100.0
                            --     * (SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))
                            --         / SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)))
                            --     * (1.0 - (SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE))
                            --                / SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))))
                            --     * ((SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                            --          + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                            --          + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))
                            --         / (SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE))
                            --             + SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE))
                            --             + SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE))))
                            --     * (1.0 - ((SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE))
                            --                 + SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE))
                            --                 + SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)))
                            --                / (SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                            --                    + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                            --                    + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))))
                            -- END AS CSSR_HUAWEI
                            

                            ,100 * (SUM(CELL_KPI_SD_SUCC
                            ) / SUM(CELL_KPI_SD_REQ)) * 
                        (1 - (SUM(CELL_SD_CALL_DROPS) / SUM(CELL_KPI_SD_SUCC))) * 
                        (SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)) /
                        (SUM(CELL_KPI_TCH_REQ_SIG) + SUM(CELL_KPI_TCH_ASS_REQ_TRAF) + SUM(CELL_KPI_TCH_HO_REQ_TRAF)) *
                        (1 - (((sum(CELL_KPI_TCH_DROPS_SIG)+sum(CELL_KPI_TCH_STATIC_DROPS_TRAF)+sum(CELL_KPI_TCH_HO_DROPS_TRAF))) /
                            ((sum(CELL_KPI_TCH_SUCC_SIG)+sum(CELL_KPI_TCH_ASS_SUCC_TRAF)+sum(CELL_KPI_TCH_HO_SUCC_TRAF))))) AS  CSSR_HUAWEI,

                            -- ARCEP 2G CALL DROP RATE - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0),
                                0
                            ) AS CDR_HUAWEI,

                            -- ARCEP 2G CALL BLOCKING RATE - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_CONG_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS CBR_HUAWEI,

                            -- TCH Congestion Rate - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS TCH_CONGESTION_RATE_HUAWEI,

                            -- SDCCH Congestion Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_KPI_SD_CONGEST AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_HUAWEI,

                            -- SDCCH Drop Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_IMM_ASS_SUCC_SD AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_HUAWEI,

                            -- ARCEP TCH Assignment Success Rate - HUAWEI (Vendor-specific)
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,

                            -- SDCCH Traffic (Erlangs) - HUAWEI
                            COALESCE(SUM(CAST(CELL_KPI_SD_TRAF_ERL AS DOUBLE)), 0) AS SDCCH_TRAFFIC_HUAWEI,

                            -- 2G Availability Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0), 0) AS CELL_AVAILABILITY_RATE_HUAWEI,


                                COALESCE(SUM(CAST(CELL_KPI_TCH_TRAF_ERL_TRAF AS DOUBLE)), 0) TRAFFIC_VOIX_HUAWEI,
                                -- handover sr
                                100.0 * (
                        (COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_SUCC AS DOUBLE)), 0)
                        + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_SUCC AS DOUBLE)), 0))
                        / NULLIF(
                            COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_CMD AS DOUBLE)), 0)
                            + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_CMD AS DOUBLE)), 0),
                            0
                            )
                        ) AS HANDOVER_SUCCESS_RATE_HUAWEI



                            FROM
                            hourly_huawei_2g_all_counters h
                            -- LEFT JOIN
                            --   EPT_2G ept ON h.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'

                            WHERE
                            -- h.date BETWEEN '2026-01-26' AND '2026-01-26'  -- Adjust date range as needed
                                {huawei__where_clause}
                            GROUP BY
                            {huawei__group_by}
                        ),

                        ERICSSON_2G_KPI AS (
                            SELECT
                            {eric__select_fields}
                            -- e.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT,

                            -- CSSR (Call Setup Success Rate) - ERICSSON
                            ,CASE
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
                            COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) TRAFFIC_VOIX_ERICSSON
                            FROM
                            hourly_ericsson_arcep_2g_counters e
                            -- LEFT JOIN
                            --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

                            WHERE
                            -- e.DATE BETWEEN '2026-01-28' AND '2026-01-29'  -- Adjust date range as needed
                                {eric__where_clause}

                            GROUP BY
                            {eric__group_by}
                        )



                        

                        SELECT
                        {combined__select_fields}

                        -- Location Info
                        -- COALESCE(h.SITE_NAME, e.SITE_NAME) AS SITE_NAME,
                        -- COALESCE(h.ARRONDISSEMENT, e.ARRONDISSEMENT) AS ARRONDISSEMENT,
                        -- COALESCE(h.COMMUNE, e.COMMUNE) AS COMMUNE,
                        -- COALESCE(h.DEPARTEMENT, e.DEPARTEMENT) AS DEPARTEMENT,

                        -- Vendor-specific KPIs
                        ,h.CSSR_HUAWEI,
                        -- h.CSSR_HUAWEI_2,
                        e.CSSR_ERICSSON,
                        h.CDR_HUAWEI,
                        e.CDR_ERICSSON,
                        h.CBR_HUAWEI,
                        e.CBR_ERICSSON,
                        h.TCH_CONGESTION_RATE_HUAWEI,
                        e.TCH_CONGESTION_RATE_ERICSSON,
                        h.SDCCH_CONGESTION_RATE_HUAWEI,
                        e.SDCCH_CONGESTION_RATE_ERICSSON,
                        h.SDCCH_DROP_RATE_HUAWEI,
                        e.SDCCH_DROP_RATE_ERICSSON,
                        h.SDCCH_TRAFFIC_HUAWEI,
                        e.SDCCH_TRAFFIC_ERICSSON,
                        h.CELL_AVAILABILITY_RATE_HUAWEI,
                        e.CELL_AVAILABILITY_RATE_ERICSSON,

                        h.TRAFFIC_VOIX_HUAWEI,
                        e.TRAFFIC_VOIX_ERICSSON,

                        -- Vendor-specific only
                        h.TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,
                        e.TCH_AVAILABILITY_RATE_ERICSSON,
                        e.DOWNTIME_MANUAL,
                        e.SDCCH_BLOCKING_RATE_ERICSSON,

                        h.HANDOVER_SUCCESS_RATE_HUAWEI,

                        -- Network-level weighted averages (0.22 Huawei + 0.78 Ericsson)
                        (COALESCE(h.CSSR_HUAWEI, 0) * 0.22) + (COALESCE(e.CSSR_ERICSSON, 0) * 0.78) AS CSSR_NETWORK,
                        (COALESCE(h.CDR_HUAWEI, 0) * 0.22) + (COALESCE(e.CDR_ERICSSON, 0) * 0.78) AS CDR_NETWORK,
                        (COALESCE(h.CBR_HUAWEI, 0) * 0.22) + (COALESCE(e.CBR_ERICSSON, 0) * 0.78) AS CBR_NETWORK,
                        (COALESCE(h.TCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.TCH_CONGESTION_RATE_ERICSSON, 0) * 0.78) AS TCH_CONGESTION_RATE_NETWORK,
                        (COALESCE(h.SDCCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.SDCCH_CONGESTION_RATE_ERICSSON, 0) * 0.78) AS SDCCH_CONGESTION_RATE_NETWORK,
                        (COALESCE(h.SDCCH_DROP_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.SDCCH_DROP_RATE_ERICSSON, 0) * 0.78) AS SDCCH_DROP_RATE_NETWORK,
                        (COALESCE(h.SDCCH_TRAFFIC_HUAWEI, 0) * 0.22) + (COALESCE(e.SDCCH_TRAFFIC_ERICSSON, 0) * 0.78) AS SDCCH_TRAFFIC_NETWORK,
                        (COALESCE(h.CELL_AVAILABILITY_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.CELL_AVAILABILITY_RATE_ERICSSON, 0) * 0.78) AS CELL_AVAILABILITY_RATE_NETWORK,
                        h.TRAFFIC_VOIX_HUAWEI + e.TRAFFIC_VOIX_ERICSSON AS TRAFFIC_NETWORK

                        FROM HUAWEI_2G_KPI h
                        LEFT JOIN ERICSSON_2G_KPI e
                        ON {eric__huawei__join_on}
                    """
                }

            }
            

        },


        "3G": {

            "ERICSSON": {
                
                
                "PACKET_LOSS_BB": {
                    "query_type": "raw_sql",
                    "description": "3G  PACKET LOSS  ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "SITE_NAME": "ept.SITE_NAME",
                                "COMMUNE": "ept.COMMUNE",
                                "ARRONDISSEMENT": "ept.ARRONDISSEMENT",
                                "DEPARTEMENT": "ept.DEPARTEMENT",
                            }
                        },

                        # "ept3g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "SITE_NAME": "e.SITE_NAME",
                        #         "ARRONDISSEMENT": "e.ARRONDISSEMENT"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "ept2g",
                            #"include_date": True,       # Always include date
                            #"include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                
                        SELECT
                    {eric__select_fields}

                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                                -- ept.COMMUNE,
                            -- ept.DEPARTEMENT,.
                        
                        
                        100.0 * SUM(CAST(sctpAssocRtxChunks AS DOUBLE))
                            / NULLIF(SUM(CAST(sctpAssocOutDataChunks AS DOUBLE)) + SUM(CAST(sctpAssocRtxChunks AS DOUBLE)), 0)
                            AS packet_loss_3g_bb 
                        FROM hourly_ericsson_packet_loss_bb_3g_counters e
                        LEFT JOIN
                                EPT_3G ept ON e.site_name = ept.site_name AND ept.VENDOR = 'ERICSSON'
                                where {eric__where_clause}
                        GROUP BY 
                        {eric__group_by}
                            DATE
                            , TIME
                            -- , SITE_NAME
                                -- ,ept.SITE_NAME
                            -- ,ept.ARRONDISSEMENT
                                -- ,ept.COMMUNE
                            -- ,ept.DEPARTEMENT
                            -- LIMIT 100
        

                    """

                }
                
                ,     
                
                "MAIN_KPIS": {
                    "query_type": "raw_sql",
                    "description": "2G Network KPIs HUAWEI ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {

                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "CELL_NAME": "e.CELL_NAME",
                                "SITE_NAME": "ePT.SITE_NAME",
                                "COMMUNE": "ePT.COMMUNE",
                                "ARRONDISSEMENT": "ept.ARRONDISSEMENT",
                                "DEPARTEMENT": "ept.DEPARTEMENT",
                            }
                        },

                        # "ept2g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "cell_name": "e.CELL_NAME",
                        #         "site_name": "e.SITE_NAME",
                        #         "commune": "e.COMMUNE"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    # "joins": [
                    #     {
                    #         "left": "eric",
                    #         "right": "ept2g",
                    #         #"include_date": True,       # Always include date
                    #         #"include_time": True,       # Only if HOURLY granularity
                    #         "include_aggregation": True, # Only if aggregation is selected
                    #         "custom": []                 # Extra static conditions if needed
                    #     }
                    # ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                    SELECT
                    {eric__select_fields}
                    -- DATE,
                    -- TIME,
                    -- , CELL_NAME,
                    -- SITE_NAME,
                    -- CONTROLLER_NAME,

                    -- CS_CSSR (Circuit-Switched Call Setup Success Rate)
                    ,100.0 *
                    (COALESCE(SUM(CAST(ReqCsSucc AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(ReqCs AS DOUBLE)), 0), 0)) *
                    (COALESCE(SUM(CAST(pmNoRabEstablishSuccessSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoRabEstablishAttemptSpeech AS DOUBLE)), 0) -
                            COALESCE(SUM(CAST(pmNoDirRetryAtt AS DOUBLE)), 0), 0)) *
                    (COALESCE(SUM(CAST(pmNoNormalRabReleaseSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoNormalRabReleaseSpeech AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoSystemRabReleaseSpeech AS DOUBLE)), 0), 0)) AS CS_CSSR,

                    -- CS_DROP (Circuit-Switched Drop Rate)
                    100.0 * (COALESCE(SUM(CAST(pmNoSystemRabReleaseSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoSystemRabReleaseSpeech AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoNormalRabReleaseSpeech AS DOUBLE)), 0), 0)) AS CS_DROP,

                    -- CS_CBR (Circuit-Switched Call Block Rate)
                    100.0 * (COALESCE(SUM(CAST(pmNoRabEstBlockTnSpeech AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoRabEstBlockNodeSpeechBest AS DOUBLE)), 0)) /
                    NULLIF(COALESCE(SUM(CAST(pmNoRabEstablishAttemptSpeech AS DOUBLE)), 0) -
                            COALESCE(SUM(CAST(pmNoRabEstablishSuccessSpeech AS DOUBLE)), 0), 0) AS CS_CBR,

                    -- PS_CSSR (Packet-Switched Call Setup Success Rate)
                    100.0 *
                    (COALESCE(SUM(CAST(ReqPsSucc AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(ReqPs AS DOUBLE)), 0) -
                            COALESCE(SUM(CAST(pmNoLoadSharingRrcConnPs AS DOUBLE)), 0), 0)) *
                    (COALESCE(SUM(CAST(pmNoRabEstablishSuccessPacketInteractive AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoRabEstablishAttemptPacketInteractive AS DOUBLE)), 0), 0)) AS PS_CSSR,

                    -- PS_DROP (Packet-Switched Drop Rate)
                    100.0 * (COALESCE(SUM(CAST(pmNoSystemRabReleasePacket AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoNormalRabReleasePacket AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmPsIntHsToFachSucc AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoSuccRbReconfOrigPsIntDch AS DOUBLE)), 0), 0)) AS PS_DROP,

                    -- DEBIT_DL (Download Throughput in kbps)
                    COALESCE(SUM(CAST(pmSumHsDlRlcUserPacketThp AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmSamplesHsDlRlcUserPacketThp AS DOUBLE)), 0), 0) AS DEBIT_DL,

                    -- DEBIT_UL (Upload Throughput in kbps)
                    COALESCE(SUM(CAST(pmSumEulRlcUserPacketThp AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmSamplesEulRlcUserPacketThp AS DOUBLE)), 0), 0) AS DEBIT_UL,

                    SUM(CAST(pmSumEulRlcTotPacketThp AS DOUBLE)) / 
                    NULLIF(SUM(CAST(pmSamplesEulRlcTotPacketThp AS DOUBLE)), 0) AS DEBIT_UL_CELL_ARCEP,

                    -- CELL_AVAILABILITY (Cell Availability Rate)
                    100.0 * (COALESCE(SUM(CAST(PERIOD_DURATION AS DOUBLE)), 0) * 60 -
                            COALESCE(SUM(CAST(pmCellDowntimeAuto AS DOUBLE)), 0)) /
                    NULLIF(COALESCE(SUM(CAST(PERIOD_DURATION AS DOUBLE)), 0) * 60, 0) AS CELL_AVAILABILITY,

                    -- RL_ADD_SUCCESS_RATE (Radio Link Addition Success Rate)
                    100.0 * COALESCE(SUM(CAST(pmRlAddSuccessBestCellSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmRlAddAttemptsBestCellSpeech AS DOUBLE)), 0), 0) AS RL_ADD_SUCCESS_RATE,

                    -- IRAT_HO_SUCCESS_RATE (Inter-RAT Handover Success Rate)
                    100.0 * COALESCE(SUM(CAST(pmNoSuccessOutIratHoSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoAttOutIratHoSpeech AS DOUBLE)), 0), 0) AS IRAT_HO_SUCCESS_RATE,

                    COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0)TRAFFIC_VOIX,
                    COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) TRAFFIC_DATA_GB

                    FROM
                    hourly_ericsson_arcep_3g_counters e
                    LEFT JOIN
                    EPT_3G ept ON e.cell_name = ept.cell_name AND ept.VENDOR = 'ERICSSON'
                    where {eric__where_clause}

                    GROUP BY
                    {eric__group_by}
                    -- DATE,
                    -- TIME
                    -- `CELL_NAME,
                    -- SITE_NAME,
                    -- CONTROLLER_NAME
                    """
                }
                
            }

            ,

            
            "HUAWEI": {
                
                
                "PACKET_LOSS_BB": {
                    "query_type": "raw_sql",
                    "description": "3G  PACKET LOSS  ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "SITE_NAME": "ept.SITE_NAME",
                                "COMMUNE": "ept.COMMUNE",
                                "ARRONDISSEMENT": "ept.ARRONDISSEMENT",
                                "DEPARTEMENT": "ept.DEPARTEMENT",
                            }
                        },

                        # "ept3g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "SITE_NAME": "e.SITE_NAME",
                        #         "ARRONDISSEMENT": "e.ARRONDISSEMENT"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "ept2g",
                            #"include_date": True,       # Always include date
                            #"include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                
                        SELECT 
                            DATE,
                            TIME,
                            controller_name,
                            ha.site_name,
                            e.commune,
                            e.arrondissement,
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
                        WHERE DATE BETWEEN '2026-02-28' AND '2026-02-28'
                        GROUP BY 
                            DATE,
                            TIME,
                            ha.site_name,
                            controller_name,
                            e.commune,
                            e.arrondissement
                        LIMIT 10;
        

                    """

                }
                
                ,     
                
                "MAIN_KPIS": {
                    "query_type": "raw_sql",
                    "description": "2G Network KPIs HUAWEI ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {

                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "CELL_NAME": "e.CELL_NAME",
                                "SITE_NAME": "ePT.SITE_NAME",
                                "COMMUNE": "ePT.COMMUNE",
                                "ARRONDISSEMENT": "ept.ARRONDISSEMENT",
                                "DEPARTEMENT": "ept.DEPARTEMENT",
                            }
                        },

                        # "ept2g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "cell_name": "e.CELL_NAME",
                        #         "site_name": "e.SITE_NAME",
                        #         "commune": "e.COMMUNE"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    # "joins": [
                    #     {
                    #         "left": "eric",
                    #         "right": "ept2g",
                    #         #"include_date": True,       # Always include date
                    #         #"include_time": True,       # Only if HOURLY granularity
                    #         "include_aggregation": True, # Only if aggregation is selected
                    #         "custom": []                 # Extra static conditions if needed
                    #     }
                    # ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                    SELECT
                    {eric__select_fields}
                    -- DATE,
                    -- TIME,
                    -- , CELL_NAME,
                    -- SITE_NAME,
                    -- CONTROLLER_NAME,

                    -- CS_CSSR (Circuit-Switched Call Setup Success Rate)
                    ,100.0 *
                    (COALESCE(SUM(CAST(ReqCsSucc AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(ReqCs AS DOUBLE)), 0), 0)) *
                    (COALESCE(SUM(CAST(pmNoRabEstablishSuccessSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoRabEstablishAttemptSpeech AS DOUBLE)), 0) -
                            COALESCE(SUM(CAST(pmNoDirRetryAtt AS DOUBLE)), 0), 0)) *
                    (COALESCE(SUM(CAST(pmNoNormalRabReleaseSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoNormalRabReleaseSpeech AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoSystemRabReleaseSpeech AS DOUBLE)), 0), 0)) AS CS_CSSR,

                    -- CS_DROP (Circuit-Switched Drop Rate)
                    100.0 * (COALESCE(SUM(CAST(pmNoSystemRabReleaseSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoSystemRabReleaseSpeech AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoNormalRabReleaseSpeech AS DOUBLE)), 0), 0)) AS CS_DROP,

                    -- CS_CBR (Circuit-Switched Call Block Rate)
                    100.0 * (COALESCE(SUM(CAST(pmNoRabEstBlockTnSpeech AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoRabEstBlockNodeSpeechBest AS DOUBLE)), 0)) /
                    NULLIF(COALESCE(SUM(CAST(pmNoRabEstablishAttemptSpeech AS DOUBLE)), 0) -
                            COALESCE(SUM(CAST(pmNoRabEstablishSuccessSpeech AS DOUBLE)), 0), 0) AS CS_CBR,

                    -- PS_CSSR (Packet-Switched Call Setup Success Rate)
                    100.0 *
                    (COALESCE(SUM(CAST(ReqPsSucc AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(ReqPs AS DOUBLE)), 0) -
                            COALESCE(SUM(CAST(pmNoLoadSharingRrcConnPs AS DOUBLE)), 0), 0)) *
                    (COALESCE(SUM(CAST(pmNoRabEstablishSuccessPacketInteractive AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoRabEstablishAttemptPacketInteractive AS DOUBLE)), 0), 0)) AS PS_CSSR,

                    -- PS_DROP (Packet-Switched Drop Rate)
                    100.0 * (COALESCE(SUM(CAST(pmNoSystemRabReleasePacket AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoNormalRabReleasePacket AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmPsIntHsToFachSucc AS DOUBLE)), 0) +
                            COALESCE(SUM(CAST(pmNoSuccRbReconfOrigPsIntDch AS DOUBLE)), 0), 0)) AS PS_DROP,

                    -- DEBIT_DL (Download Throughput in kbps)
                    COALESCE(SUM(CAST(pmSumHsDlRlcUserPacketThp AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmSamplesHsDlRlcUserPacketThp AS DOUBLE)), 0), 0) AS DEBIT_DL,

                    -- DEBIT_UL (Upload Throughput in kbps)
                    COALESCE(SUM(CAST(pmSumEulRlcUserPacketThp AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmSamplesEulRlcUserPacketThp AS DOUBLE)), 0), 0) AS DEBIT_UL,

                    SUM(CAST(pmSumEulRlcTotPacketThp AS DOUBLE)) / 
                    NULLIF(SUM(CAST(pmSamplesEulRlcTotPacketThp AS DOUBLE)), 0) AS DEBIT_UL_CELL_ARCEP,

                    -- CELL_AVAILABILITY (Cell Availability Rate)
                    100.0 * (COALESCE(SUM(CAST(PERIOD_DURATION AS DOUBLE)), 0) * 60 -
                            COALESCE(SUM(CAST(pmCellDowntimeAuto AS DOUBLE)), 0)) /
                    NULLIF(COALESCE(SUM(CAST(PERIOD_DURATION AS DOUBLE)), 0) * 60, 0) AS CELL_AVAILABILITY,

                    -- RL_ADD_SUCCESS_RATE (Radio Link Addition Success Rate)
                    100.0 * COALESCE(SUM(CAST(pmRlAddSuccessBestCellSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmRlAddAttemptsBestCellSpeech AS DOUBLE)), 0), 0) AS RL_ADD_SUCCESS_RATE,

                    -- IRAT_HO_SUCCESS_RATE (Inter-RAT Handover Success Rate)
                    100.0 * COALESCE(SUM(CAST(pmNoSuccessOutIratHoSpeech AS DOUBLE)), 0) /
                    NULLIF(COALESCE(SUM(CAST(pmNoAttOutIratHoSpeech AS DOUBLE)), 0), 0) AS IRAT_HO_SUCCESS_RATE,

                    COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0)TRAFFIC_VOIX,
                    COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) TRAFFIC_DATA_GB

                    FROM
                    hourly_ericsson_arcep_3g_counters e
                    LEFT JOIN
                    EPT_3G ept ON e.cell_name = ept.cell_name AND ept.VENDOR = 'ERICSSON'
                    where {eric__where_clause}

                    GROUP BY
                    {eric__group_by}
                    -- DATE,
                    -- TIME
                    -- `CELL_NAME,
                    -- SITE_NAME,
                    -- CONTROLLER_NAME
                    """
                }
                
            }

            ,
    
        },


        "4G": {

            "ERICSSON": {
                
                "PACKET_LOSS_BB": {
                    "query_type": "raw_sql",
                    "description": "3G  PACKET LOSS  ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {

                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "SITE_NAME": "ept.SITE_NAME",
                                "COMMUNE": "ept.COMMUNE",
                                "ARRONDISSEMENT": "ept.ARRONDISSEMENT",
                                "DEPARTEMENT": "ept.DEPARTEMENT",
                            }
                        },

                        # "ept3g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "SITE_NAME": "e.SITE_NAME",
                        #         "ARRONDISSEMENT": "e.ARRONDISSEMENT"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "ept2g",
                            #"include_date": True,       # Always include date
                            #"include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                
                    SELECT
                        -- DATE,
                        -- TIME,
                        -- SITE_NAME,
                        {eric__select_fields}
                        100.0 * SUM(CAST(sctpAssocRtxChunks AS DOUBLE))
                            / NULLIF(SUM(CAST(sctpAssocOutDataChunks AS DOUBLE)) + SUM(CAST(sctpAssocRtxChunks AS DOUBLE)), 0)
                            AS packet_loss_4g_bb
                        FROM hourly_ericsson_packet_loss_bb_4g_counters
                        LEFT JOIN
                        EPT_4G ept ON e.site_name = ept.site_name AND ept.VENDOR = 'ERICSSON'
                        where {eric__where_clause}
                        GROUP BY 
                        {eric__group_by}
                        -- DATE, TIME, SITE_NAME

                    """

                }
                
                ,     
                
                "MAIN_KPIS": {
                    "query_type": "raw_sql",
                    "description": "2G Network KPIs HUAWEI ERICSSON",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "CELL_NAME": "e.CELL_NAME",
                                "SITE_NAME": "ePT.SITE_NAME",
                                "COMMUNE": "ePT.COMMUNE",
                                "ARRONDISSEMENT": "ept.ARRONDISSEMENT",
                                "DEPARTEMENT": "ept.DEPARTEMENT",
                            }
                        },

                        # "ept2g":{
                        #     "no_date": True,
                        #     "no_time": True,
                        #     "aggregations": {
                        #         "cell_name": "e.CELL_NAME",
                        #         "site_name": "e.SITE_NAME",
                        #         "commune": "e.COMMUNE"
                        #     }
                        # },

                        # "huawei": {
                        #     "date_col": "h.date",
                        #     "time_col": "h.time",
                        #     "aggregations": {
                        #     }
                        # },
                        # "combined":{
                        #     "date_col": "COALESCE(h.date, e.DATE)",
                        #     "time_col": "COALESCE(h.time, e.TIME)",
                        #     "aggregations": {
                        #     }
                        # }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    # "joins": [
                    #     {
                    #         "left": "eric",
                    #         "right": "ept2g",
                    #         #"include_date": True,       # Always include date
                    #         #"include_time": True,       # Only if HOURLY granularity
                    #         "include_aggregation": True, # Only if aggregation is selected
                    #         "custom": []                 # Extra static conditions if needed
                    #     }
                    # ],

                    "chart_configs": {
                        

                    },

                    "sql_template": """
                    
                        SELECT
                        {eric__select_fields}

                        -- PS_CSSR: LTE ERAB Setup Success Rate (%)
                    , 100.0 * (
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

                        -- UL_USER_THP: UL User Throughput (kbps)
                        -- COALESCE(SUM(CAST(pmPdcpVolUlDrb AS DOUBLE)), 0) /
                        -- NULLIF(COALESCE(SUM(CAST(pmUeThpTimeUl AS DOUBLE)), 0) / 1000, 0) AS UL_USER_THP,

                        -- new one
                            COALESCE(SUM(CAST(pmUeThpVolUl AS DOUBLE)), 0) /
                        NULLIF(COALESCE(SUM(CAST(pmUeThpTimeUl AS DOUBLE)), 0) / 1000, 0) AS UL_USER_THP,

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
                            ) / NULLIF(COALESCE(SUM(PERIOD_DURATION), 0) * 60, 0)
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
                        COALESCE(SUM(CAST(pmRrcConnMax AS DOUBLE)), 0) AS USER_CONNECTED,
                        COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) AS TRAFFIC_DATA_GB


                        FROM hourly_ericsson_arcep_4g_counters e

                        LEFT JOIN EPT_4G  EPT
                        ON e.CELL_NAME = EPT.CELL_NAME
                        AND EPT.VENDOR = 'ERICSSON'

                        WHERE {eric__where_clause} 

                        GROUP BY 
                        {eric__group_by}
                        -- DATE, TIME


                    """

                }
                
            }

            ,
    
        },


        


        "GENERAL": {
            "NETWORK_HEALTH": {
                "description": "General network health across all technologies",
                "date_time_filters": ["start_date", "end_date"],
                "parameters": ["technology"],
                "aggregation_levels": {
                    "technology": "m.technology",
                    "vendor": "m.vendor",
                    "controller": "m.controller"
                },
                "time_granularities": {
                    "DAILY": {"is_available": True, "date_field": "m.date", "time_field": None},
                    "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(m.date, 1)", "time_field": None},
                    "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(m.date, '%Y-%m')", "time_field": None}
                },
                "kpi_fields": {
                    "Total_Sites": "COUNT(DISTINCT site_name)",
                    "Avg_Availability": "AVG(availability)"
                },
                "sql_template": """
                    SELECT {fields}
                    FROM network_health_summary m
                    WHERE {where_conditions}
                    {group_by}
                    ORDER BY {order_by}
                """
            }
        },

        "2G_NETWORK": {

            "COMBINED": {

                "KPI_MONITORING": {
                    "query_type": "multi_cte",
                    "description": "2G Network KPI - Combined Vendors",
                    "date_time_filters": ["start_date", "end_date", "multiple_date"],

                    # Subqueries configuration
                    "subqueries": [
                        {
                            "name": "HUAWEI2G_KPI",
                            "table": "daily_arcep_huawei_2g",
                            "alias": "h",
                            "time_granularities": {
                                "HOURLY": {"is_available": True, "date_field": "DATE", "time_field": "TIME"},
                                "DAILY": {"is_available": True, "date_field": "DATE", "time_field": None},
                                "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(DATE, 1)", "time_field": None},
                                "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(DATE, '%Y-%m')", "time_field": None}
                            },
                            "aggregation_levels": {},
                            "kpi_fields": {
                                "CSSR_HUAWEI": """100 * (SUM(Suc_SDCCH_Seiz) / NULLIF(SUM(SDCCH_Seiz_Req), 0)) *
                                    (1 - (SUM(SDCCHDrop) / NULLIF(SUM(Suc_SDCCH_Seiz), 0))) *
                                    (SUM(Suc_TCH_Seiz_SG) + SUM(Suc_TCH_Seiz_TrafChann) + SUM(Suc_TCH_Seiz_handTrafChan)) /
                                    NULLIF((SUM(TCH_Seizure_Req_SC) + SUM(TCH_Seiz_Req_TrafChan) + SUM(TCH_Seiz_Req_HandTrafChan)), 0) *
                                    (1 - (SUM(TCHDrop_Nume_ARCEP) / NULLIF(SUM(TCHDrop_Deno_ARCEP), 0)))""",
                                "CDR_HUAWEI": "(100 * SUM(TCHDrop_Nume_ARCEP) / NULLIF(SUM(TCHDrop_Deno_ARCEP), 0))",
                                "CBR_HUAWEI": "100 * (SUM(TCHCONG_Nume_ARCEP) / NULLIF(SUM(TCHCONG_Deno_ARCEP), 0))"
                            },
                            "sql_template": """
                                SELECT {fields}
                                FROM {table} {alias}
                                WHERE {where_conditions}
                                {group_by}
                            """
                        },
                        {
                            "name": "ERICSSON_2GKPI",
                            "table": "daily_arcep_ericsson_2g",
                            "alias": "e",
                            "time_granularities": {
                                "HOURLY": {"is_available": True, "date_field": "DATE", "time_field": "TIME"},
                                "DAILY": {"is_available": True, "date_field": "DATE_id", "time_field": None},
                                "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(DATE_id, 1)", "time_field": None},
                                "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(DATE_id, '%Y-%m')", "time_field": None}
                            },
                            "aggregation_levels": {},
                            "kpi_fields": {
                                "CSSR_ERICSSON": """(100 * (1 - (SUM(CCONGS) / NULLIF(SUM(CCALLS), 0)))) *
                                    (1 - ((SUM(CNDROP) - SUM(CNRELCONG)) / NULLIF(SUM(CMSESTAB), 0))) *
                                    (SUM(TCASSALL) / NULLIF(SUM(TASSALL), 0)) *
                                    (1 - (((SUM(TFNDROP) + SUM(THNDROP) + SUM(TFNDROPSUB) + SUM(THNDROPSUB)) /
                                    NULLIF((SUM(TFCASSALL) + SUM(THCASSALL) + SUM(TFCASSALLSUB) + SUM(THCASSALLSUB)), 0) * 100) / 100))""",
                                "CBR_ERICSSON": "(100 * (SUM(CNRELCONG) + SUM(THNRELCONG) + SUM(TFNRELCONG)) / NULLIF(SUM(TASSALL), 0))",
                                "CDR_ERICSSON": "(100 * (SUM(TFNDROP) + SUM(THNDROP) + SUM(TFNDROPSUB) + SUM(THNDROPSUB)) / NULLIF((SUM(TFCASSALL) + SUM(THCASSALL) + SUM(TFCASSALLSUB) + SUM(THCASSALLSUB)), 0))"
                            },
                            "sql_template": """
                                SELECT {fields}
                                FROM {table} {alias}
                                WHERE {where_conditions}
                                {group_by}
                            """
                        }
                    ],

                    # How to join the CTEs
                    "cte_joins": [
                        {
                            "type": "LEFT JOIN",
                            "left": "HUAWEI2G_KPI",
                            "right": "ERICSSON_2GKPI",
                            "on": ["HUAWEI2G_KPI.date = ERICSSON_2GKPI.DATE"]
                        }
                    ],

                    # Outer query configuration (what the client controls)
                    "time_granularities": {
                        "HOURLY": {"is_available": True, "date_field": "DATE", "time_field": "TIME"},
                        "DAILY": {"is_available": True, "date_field": "HUAWEI2G_KPI.date", "time_field": None},
                        "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(HUAWEI2G_KPI.date, 1)", "time_field": None},
                        "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(HUAWEI2G_KPI.date, '%Y-%m')", "time_field": None}
                    },

                    "aggregation_levels": {
                    },

                    "kpi_fields": {
                        "CSSR_HUAWEI": "HUAWEI2G_KPI.CSSR_HUAWEI",
                        "CDR_HUAWEI": "HUAWEI2G_KPI.CDR_HUAWEI",
                        "CBR_HUAWEI": "HUAWEI2G_KPI.CBR_HUAWEI",
                        "CSSR_ERICSSON": "ERICSSON_2GKPI.CSSR_ERICSSON",
                        "CDR_ERICSSON": "ERICSSON_2GKPI.CDR_ERICSSON",
                        "CBR_ERICSSON": "ERICSSON_2GKPI.CBR_ERICSSON",
                        "CSSR_NETWORK": "(HUAWEI2G_KPI.CSSR_HUAWEI * 0.22) + (ERICSSON_2GKPI.CSSR_ERICSSON * 0.78)",
                        "CDR_NETWORK": "(HUAWEI2G_KPI.CDR_HUAWEI * 0.22) + (ERICSSON_2GKPI.CDR_ERICSSON * 0.78)",
                        "CBR_NETWORK": "(HUAWEI2G_KPI.CBR_HUAWEI * 0.22) + (ERICSSON_2GKPI.CBR_ERICSSON * 0.78)"
                    },

                    "sql_template": """
                        SELECT {fields}
                        FROM {cte_joins}
                        {group_by}
                        {order_by}
                    """
                }

            },

            "COMBINED_2": {

                "KPI_MONITORING": {
                    "query_type": "multi_cte",
                    "description": "2G Network KPI - Combined Vendors (Hourly with All KPIs)",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    # Subqueries configuration
                    "subqueries": [
                        {
                            "name": "HUAWEI_2G_KPI",
                            "table": "hourly_huawei_2g_all_counters",
                            "alias": "h",
                            "time_granularities": {
                                "HOURLY": {"is_available": True, "date_field": "date", "time_field": "TIME_FORMAT(time, '%H:%i:%s')"},
                                "DAILY": {"is_available": True, "date_field": "date", "time_field": None},
                                "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(date, 1)", "time_field": None},
                                "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(date, '%Y-%m')", "time_field": None}
                            },
                            "aggregation_levels": {},
                            "kpi_fields": {
                                "CSSR_HUAWEI": """CASE
                                    WHEN COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) = 0
                                    OR COALESCE(SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)), 0) = 0
                                    OR (COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)) = 0
                                    OR (COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)) = 0
                                    THEN 0
                                    ELSE
                                    100.0
                                    * (SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)) / SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)))
                                    * (1.0 - (SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)) / SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))))
                                    * ((SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                                        + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                                        + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))
                                        / (SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE))
                                            + SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE))
                                            + SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE))))
                                    * (1.0 - ((SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE))
                                                + SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE))
                                                + SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)))
                                                / (SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                                                    + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                                                    + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))))
                                END""",
                                "CDR_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "CBR_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_CONG_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "TCH_CONGESTION_RATE_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "SDCCH_CONGESTION_RATE_HUAWEI": """100.0 * COALESCE(SUM(CAST(CELL_KPI_SD_CONGEST AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_DROP_RATE_HUAWEI": """100.0 * COALESCE(SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CELL_IMM_ASS_SUCC_SD AS DOUBLE)), 0) + 1e-7)""",
                                "TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "SDCCH_TRAFFIC_HUAWEI": """COALESCE(SUM(CAST(CELL_KPI_SD_TRAF_ERL AS DOUBLE)), 0)""",
                                "CELL_AVAILABILITY_RATE_HUAWEI": """100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0) + 1e-7)"""
                            },
                            "sql_template": """
                                SELECT {fields}
                                FROM {table} {alias}
                                WHERE {where_conditions}
                                {group_by}
                            """
                        },
                        {
                            "name": "ERICSSON_2G_KPI",
                            "table": "hourly_ericsson_arcep_2g_counters",
                            "alias": "e",
                            "time_granularities": {
                                "HOURLY": {"is_available": True, "date_field": "DATE", "time_field": "TIME"},
                                "DAILY": {"is_available": True, "date_field": "DATE", "time_field": None},
                                "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(DATE, 1)", "time_field": None},
                                "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(DATE, '%Y-%m')", "time_field": None}
                            },
                            "aggregation_levels": {},
                            "kpi_fields": {
                                "CSSR_ERICSSON": """CASE
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
                                    * (1.0 - ((SUM(CAST(TFNDROP AS DOUBLE)) + SUM(CAST(THNDROP AS DOUBLE))
                                                + SUM(CAST(TFNDROPSUB AS DOUBLE)) + SUM(CAST(THNDROPSUB AS DOUBLE)))
                                                / (SUM(CAST(TFCASSALL AS DOUBLE)) + SUM(CAST(THCASSALL AS DOUBLE))
                                                    + SUM(CAST(TFCASSALLSUB AS DOUBLE)) + SUM(CAST(THCASSALLSUB AS DOUBLE)))))
                                END""",
                                "CBR_ERICSSON": """100.0 * (
                                    COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
                                ) / (COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) + 1e-7)""",
                                "CDR_ERICSSON": """100.0 * (
                                    COALESCE(SUM(CAST(THNDROP AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNDROPSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNDROP AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNDROPSUB AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "CELL_AVAILABILITY_RATE_ERICSSON": """100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0) + 1e-7))""",
                                "TCH_AVAILABILITY_RATE_ERICSSON": """100.0 * (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(TAVASCAN AS DOUBLE)), 0) + 1e-7)) /
                                (COALESCE(AVG(CAST(AVG_TNUCHCNT AS DOUBLE)), 1))""",
                                "DOWNTIME_MANUAL": """COALESCE(SUM(CAST(HDWNACC AS DOUBLE)), 0)""",
                                "TCH_CONGESTION_RATE_ERICSSON": """100.0 * (
                                    COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
                                ) / (COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_DROP_RATE_ERICSSON": """100.0 * COALESCE(SUM(CAST(CNDROP AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_TRAFFIC_ERICSSON": """COALESCE(SUM(CAST(CTRALACC AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CNSCAN AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_BLOCKING_RATE_ERICSSON": """100.0 * COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_CONGESTION_RATE_ERICSSON": """100.0 * (COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) + COALESCE(SUM(CAST(CCONGSSUB AS DOUBLE)), 0)) /
                                (COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) + 1e-7)"""
                            },
                            "sql_template": """
                                SELECT {fields}
                                FROM {table} {alias}
                                WHERE {where_conditions}
                                {group_by}
                            """
                        }
                    ],

                    # How to join the CTEs
                    "cte_joins": [
                        {
                            "type": "LEFT JOIN",
                            "left": "HUAWEI_2G_KPI",
                            "right": "ERICSSON_2G_KPI",
                            "on": ["HUAWEI_2G_KPI.date = ERICSSON_2G_KPI.DATE", "HUAWEI_2G_KPI.time = ERICSSON_2G_KPI.TIME"]
                        }
                    ],

                    # Outer query configuration (what the client controls)
                    "time_granularities": {
                        "HOURLY": {"is_available": True, "date_field": "HUAWEI_2G_KPI.date", "time_field": "HUAWEI_2G_KPI.time"},
                        "DAILY": {"is_available": True, "date_field": "HUAWEI_2G_KPI.date", "time_field": None},
                        "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(HUAWEI_2G_KPI.date, 1)", "time_field": None},
                        "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(HUAWEI_2G_KPI.date, '%Y-%m')", "time_field": None}
                    },

                    "aggregation_levels": {
                    },

                    "kpi_fields": {
                        "CSSR_HUAWEI": "HUAWEI_2G_KPI.CSSR_HUAWEI",
                        "CDR_HUAWEI": "HUAWEI_2G_KPI.CDR_HUAWEI",
                        "CBR_HUAWEI": "HUAWEI_2G_KPI.CBR_HUAWEI",
                        "TCH_CONGESTION_RATE_HUAWEI": "HUAWEI_2G_KPI.TCH_CONGESTION_RATE_HUAWEI",
                        "SDCCH_CONGESTION_RATE_HUAWEI": "HUAWEI_2G_KPI.SDCCH_CONGESTION_RATE_HUAWEI",
                        "SDCCH_DROP_RATE_HUAWEI": "HUAWEI_2G_KPI.SDCCH_DROP_RATE_HUAWEI",
                        "TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI": "HUAWEI_2G_KPI.TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI",
                        "SDCCH_TRAFFIC_HUAWEI": "HUAWEI_2G_KPI.SDCCH_TRAFFIC_HUAWEI",
                        "CELL_AVAILABILITY_RATE_HUAWEI": "HUAWEI_2G_KPI.CELL_AVAILABILITY_RATE_HUAWEI",

                        "CSSR_ERICSSON": "ERICSSON_2G_KPI.CSSR_ERICSSON",
                        "CDR_ERICSSON": "ERICSSON_2G_KPI.CDR_ERICSSON",
                        "CBR_ERICSSON": "ERICSSON_2G_KPI.CBR_ERICSSON",
                        "CELL_AVAILABILITY_RATE_ERICSSON": "ERICSSON_2G_KPI.CELL_AVAILABILITY_RATE_ERICSSON",
                        "TCH_AVAILABILITY_RATE_ERICSSON": "ERICSSON_2G_KPI.TCH_AVAILABILITY_RATE_ERICSSON",
                        "DOWNTIME_MANUAL": "ERICSSON_2G_KPI.DOWNTIME_MANUAL",
                        "TCH_CONGESTION_RATE_ERICSSON": "ERICSSON_2G_KPI.TCH_CONGESTION_RATE_ERICSSON",
                        "SDCCH_DROP_RATE_ERICSSON": "ERICSSON_2G_KPI.SDCCH_DROP_RATE_ERICSSON",
                        "SDCCH_TRAFFIC_ERICSSON": "ERICSSON_2G_KPI.SDCCH_TRAFFIC_ERICSSON",
                        "SDCCH_BLOCKING_RATE_ERICSSON": "ERICSSON_2G_KPI.SDCCH_BLOCKING_RATE_ERICSSON",
                        "SDCCH_CONGESTION_RATE_ERICSSON": "ERICSSON_2G_KPI.SDCCH_CONGESTION_RATE_ERICSSON",

                        "CSSR_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CSSR_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CSSR_ERICSSON, 0) * 0.78)",
                        "CDR_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CDR_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CDR_ERICSSON, 0) * 0.78)",
                        "CBR_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CBR_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CBR_ERICSSON, 0) * 0.78)",
                        "TCH_CONGESTION_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.TCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.TCH_CONGESTION_RATE_ERICSSON, 0) * 0.78)",
                        "SDCCH_CONGESTION_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.SDCCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.SDCCH_CONGESTION_RATE_ERICSSON, 0) * 0.78)",
                        "SDCCH_DROP_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.SDCCH_DROP_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.SDCCH_DROP_RATE_ERICSSON, 0) * 0.78)",
                        "SDCCH_TRAFFIC_NETWORK": "(HUAWEI_2G_KPI.SDCCH_TRAFFIC_HUAWEI) + (ERICSSON_2G_KPI.SDCCH_TRAFFIC_ERICSSON)",
                        "CELL_AVAILABILITY_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CELL_AVAILABILITY_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CELL_AVAILABILITY_RATE_ERICSSON, 0) * 0.78)"
                    },

                    "chart_configs": {
                        "CSSR_ALL": {
                            "KPIS": ["CSSR_NETWORK", "CSSR_HUAWEI", "CSSR_ERICSSON"],
                            "title": "2G CSSR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CSSR (%)",
                            "threshold": 99
                        },
                        "CDR_ALL": {
                            "KPIS": ["CDR_NETWORK", "CDR_HUAWEI", "CDR_ERICSSON"],
                            "title": "2G CDR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CDR (%)"
                        },
                        "CBR_ALL": {
                            "KPIS": ["CBR_NETWORK", "CBR_HUAWEI", "CBR_ERICSSON"],
                            "title": "2G CBR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CBR (%)",
                            "threshold": 3
                        },
                        "TCH_CONGESTION_RATE_ALL": {
                            "KPIS": ["TCH_CONGESTION_RATE_NETWORK", "TCH_CONGESTION_RATE_HUAWEI", "TCH_CONGESTION_RATE_ERICSSON"],
                            "title": "2G TCH Congestion - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "TCH Congestion (%)",
                            "threshold": 2
                        },
                        "SDCCH_CONGESTION_RATE_ALL": {
                            "KPIS": ["SDCCH_CONGESTION_RATE_NETWORK", "SDCCH_CONGESTION_RATE_HUAWEI", "SDCCH_CONGESTION_RATE_ERICSSON"],
                            "title": "2G SDCCH Congestion - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Congestion (%)",
                            "threshold": 1
                        },
                        "SDCCH_DROP_RATE_ALL": {
                            "KPIS": ["SDCCH_DROP_RATE_NETWORK", "SDCCH_DROP_RATE_HUAWEI", "SDCCH_DROP_RATE_ERICSSON"],
                            "title": "2G SDCCH Drop Rate - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Drop Rate (%)"
                        },
                        "CELL_AVAILABILITY_ALL": {
                            "KPIS": ["CELL_AVAILABILITY_RATE_NETWORK", "CELL_AVAILABILITY_RATE_HUAWEI", "CELL_AVAILABILITY_RATE_ERICSSON"],
                            "title": "2G Cell Availability - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "Availability (%)",
                            "threshold": 99
                        },
                        "SDCCH_TRAFFIC_ALL": {
                            "KPIS": ["SDCCH_TRAFFIC_NETWORK", "SDCCH_TRAFFIC_HUAWEI", "SDCCH_TRAFFIC_ERICSSON"],
                            "title": "2G SDCCH Traffic - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Traffic (Erl)"
                        },

                        "CSSR_NETWORK_vs_CDR": {
                            "KPIS": ["CSSR_NETWORK", "CDR_NETWORK"],
                            "title": "2G Network CSSR vs CDR",
                            "default_type_1": "line",
                            "default_type_2": "bar",
                            "is_dual_axis": True,
                            "y_axis_titles": ["CSSR (%)", "CDR (%)"]
                        }

                    },

                    "sql_template": """
                        SELECT {fields}
                        FROM {cte_joins}
                        {group_by}
                        {order_by}
                    """
                },

            
                "KPI_MONITORING_2": {
                    "query_type": "multi_cte",
                    "description": "3G Network KPI - Combined Vendors (Hourly with All KPIs)",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    # Subqueries configuration
                    "subqueries": [
                        {
                            "name": "HUAWEI_2G_KPI",
                            "table": "hourly_huawei_2g_all_counters",
                            "alias": "h",
                            "time_granularities": {
                                "HOURLY": {"is_available": True, "date_field": "date", "time_field": "TIME_FORMAT(time, '%H:%i:%s')"},
                                "DAILY": {"is_available": True, "date_field": "date", "time_field": None},
                                "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(date, 1)", "time_field": None},
                                "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(date, '%Y-%m')", "time_field": None}
                            },
                            "aggregation_levels": {},
                            "kpi_fields": {
                                "CSSR_HUAWEI": """CASE
                                    WHEN COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) = 0
                                    OR COALESCE(SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)), 0) = 0
                                    OR (COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)) = 0
                                    OR (COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)) = 0
                                    THEN 0
                                    ELSE
                                    100.0
                                    * (SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)) / SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)))
                                    * (1.0 - (SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)) / SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))))
                                    * ((SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                                        + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                                        + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))
                                        / (SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE))
                                            + SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE))
                                            + SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE))))
                                    * (1.0 - ((SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE))
                                                + SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE))
                                                + SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)))
                                                / (SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                                                    + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                                                    + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))))
                                END""",
                                "CDR_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "CBR_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_CONG_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "TCH_CONGESTION_RATE_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "SDCCH_CONGESTION_RATE_HUAWEI": """100.0 * COALESCE(SUM(CAST(CELL_KPI_SD_CONGEST AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_DROP_RATE_HUAWEI": """100.0 * COALESCE(SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CELL_IMM_ASS_SUCC_SD AS DOUBLE)), 0) + 1e-7)""",
                                "TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI": """100.0 * (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "SDCCH_TRAFFIC_HUAWEI": """COALESCE(SUM(CAST(CELL_KPI_SD_TRAF_ERL AS DOUBLE)), 0)""",
                                "CELL_AVAILABILITY_RATE_HUAWEI": """100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0) + 1e-7)"""
                            },
                            
                            "sql_template": """
                                SELECT {fields}
                                FROM {table} {alias}
                                WHERE {where_conditions}
                                {group_by}
                            """
                        },
                        {
                            "name": "ERICSSON_2G_KPI",
                            "table": "hourly_ericsson_arcep_2g_counters",
                            "alias": "e",
                            "time_granularities": {
                                "HOURLY": {"is_available": True, "date_field": "DATE", "time_field": "TIME"},
                                "DAILY": {"is_available": True, "date_field": "DATE", "time_field": None},
                                "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(DATE, 1)", "time_field": None},
                                "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(DATE, '%Y-%m')", "time_field": None}
                            },
                            "aggregation_levels": {},
                            "kpi_fields": {
                                "CSSR_ERICSSON": """CASE
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
                                    * (1.0 - ((SUM(CAST(TFNDROP AS DOUBLE)) + SUM(CAST(THNDROP AS DOUBLE))
                                                + SUM(CAST(TFNDROPSUB AS DOUBLE)) + SUM(CAST(THNDROPSUB AS DOUBLE)))
                                                / (SUM(CAST(TFCASSALL AS DOUBLE)) + SUM(CAST(THCASSALL AS DOUBLE))
                                                    + SUM(CAST(TFCASSALLSUB AS DOUBLE)) + SUM(CAST(THCASSALLSUB AS DOUBLE)))))
                                END""",
                                "CBR_ERICSSON": """100.0 * (
                                    COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
                                ) / (COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) + 1e-7)""",
                                "CDR_ERICSSON": """100.0 * (
                                    COALESCE(SUM(CAST(THNDROP AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNDROPSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNDROP AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNDROPSUB AS DOUBLE)), 0)
                                ) / (
                                    COALESCE(SUM(CAST(TFCASSALL AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFCASSALLSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THCASSALL AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THCASSALLSUB AS DOUBLE)), 0)
                                    + 1e-7
                                )""",
                                "CELL_AVAILABILITY_RATE_ERICSSON": """100.0 - (100.0 * COALESCE(SUM(CAST(TDWNACC AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(TDWNSCAN AS DOUBLE)), 0) + 1e-7))""",
                                "TCH_AVAILABILITY_RATE_ERICSSON": """100.0 * (COALESCE(SUM(CAST(TAVAACC AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(TAVASCAN AS DOUBLE)), 0) + 1e-7)) /
                                (COALESCE(AVG(CAST(AVG_TNUCHCNT AS DOUBLE)), 1))""",
                                "DOWNTIME_MANUAL": """COALESCE(SUM(CAST(HDWNACC AS DOUBLE)), 0)""",
                                "TCH_CONGESTION_RATE_ERICSSON": """100.0 * (
                                    COALESCE(SUM(CAST(CNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(TFNRELCONGSUB AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONG AS DOUBLE)), 0)
                                    + COALESCE(SUM(CAST(THNRELCONGSUB AS DOUBLE)), 0)
                                ) / (COALESCE(SUM(CAST(TASSALL AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_DROP_RATE_ERICSSON": """100.0 * COALESCE(SUM(CAST(CNDROP AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CMSESTAB AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_TRAFFIC_ERICSSON": """COALESCE(SUM(CAST(CTRALACC AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CNSCAN AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_BLOCKING_RATE_ERICSSON": """100.0 * COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) /
                                (COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) + 1e-7)""",
                                "SDCCH_CONGESTION_RATE_ERICSSON": """100.0 * (COALESCE(SUM(CAST(CCONGS AS DOUBLE)), 0) + COALESCE(SUM(CAST(CCONGSSUB AS DOUBLE)), 0)) /
                                (COALESCE(SUM(CAST(CCALLS AS DOUBLE)), 0) + 1e-7)"""
                            },
                            "sql_template": """
                                SELECT {fields}
                                FROM {table} {alias}
                                WHERE {where_conditions}
                                {group_by}
                            """
                        }
                    ],

                    # How to join the CTEs
                    "cte_joins": [
                        {
                            "type": "LEFT JOIN",
                            "left": "HUAWEI_2G_KPI",
                            "right": "ERICSSON_2G_KPI",
                            "on": ["HUAWEI_2G_KPI.date = ERICSSON_2G_KPI.DATE", "HUAWEI_2G_KPI.time = ERICSSON_2G_KPI.TIME"]
                        }
                    ],

                    # Outer query configuration (what the client controls)
                    "time_granularities": {
                        "HOURLY": {"is_available": True, "date_field": "HUAWEI_2G_KPI.date", "time_field": "HUAWEI_2G_KPI.time"},
                        "DAILY": {"is_available": True, "date_field": "HUAWEI_2G_KPI.date", "time_field": None},
                        "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(HUAWEI_2G_KPI.date, 1)", "time_field": None},
                        "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(HUAWEI_2G_KPI.date, '%Y-%m')", "time_field": None}
                    },

                    "aggregation_levels": {
                    },

                    "kpi_fields": {
                        "CSSR_HUAWEI": "HUAWEI_2G_KPI.CSSR_HUAWEI",
                        "CDR_HUAWEI": "HUAWEI_2G_KPI.CDR_HUAWEI",
                        "CBR_HUAWEI": "HUAWEI_2G_KPI.CBR_HUAWEI",
                        "TCH_CONGESTION_RATE_HUAWEI": "HUAWEI_2G_KPI.TCH_CONGESTION_RATE_HUAWEI",
                        "SDCCH_CONGESTION_RATE_HUAWEI": "HUAWEI_2G_KPI.SDCCH_CONGESTION_RATE_HUAWEI",
                        "SDCCH_DROP_RATE_HUAWEI": "HUAWEI_2G_KPI.SDCCH_DROP_RATE_HUAWEI",
                        "TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI": "HUAWEI_2G_KPI.TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI",
                        "SDCCH_TRAFFIC_HUAWEI": "HUAWEI_2G_KPI.SDCCH_TRAFFIC_HUAWEI",
                        "CELL_AVAILABILITY_RATE_HUAWEI": "HUAWEI_2G_KPI.CELL_AVAILABILITY_RATE_HUAWEI",

                        "CSSR_ERICSSON": "ERICSSON_2G_KPI.CSSR_ERICSSON",
                        "CDR_ERICSSON": "ERICSSON_2G_KPI.CDR_ERICSSON",
                        "CBR_ERICSSON": "ERICSSON_2G_KPI.CBR_ERICSSON",
                        "CELL_AVAILABILITY_RATE_ERICSSON": "ERICSSON_2G_KPI.CELL_AVAILABILITY_RATE_ERICSSON",
                        "TCH_AVAILABILITY_RATE_ERICSSON": "ERICSSON_2G_KPI.TCH_AVAILABILITY_RATE_ERICSSON",
                        "DOWNTIME_MANUAL": "ERICSSON_2G_KPI.DOWNTIME_MANUAL",
                        "TCH_CONGESTION_RATE_ERICSSON": "ERICSSON_2G_KPI.TCH_CONGESTION_RATE_ERICSSON",
                        "SDCCH_DROP_RATE_ERICSSON": "ERICSSON_2G_KPI.SDCCH_DROP_RATE_ERICSSON",
                        "SDCCH_TRAFFIC_ERICSSON": "ERICSSON_2G_KPI.SDCCH_TRAFFIC_ERICSSON",
                        "SDCCH_BLOCKING_RATE_ERICSSON": "ERICSSON_2G_KPI.SDCCH_BLOCKING_RATE_ERICSSON",
                        "SDCCH_CONGESTION_RATE_ERICSSON": "ERICSSON_2G_KPI.SDCCH_CONGESTION_RATE_ERICSSON",

                        "CSSR_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CSSR_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CSSR_ERICSSON, 0) * 0.78)",
                        "CDR_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CDR_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CDR_ERICSSON, 0) * 0.78)",
                        "CBR_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CBR_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CBR_ERICSSON, 0) * 0.78)",
                        "TCH_CONGESTION_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.TCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.TCH_CONGESTION_RATE_ERICSSON, 0) * 0.78)",
                        "SDCCH_CONGESTION_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.SDCCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.SDCCH_CONGESTION_RATE_ERICSSON, 0) * 0.78)",
                        "SDCCH_DROP_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.SDCCH_DROP_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.SDCCH_DROP_RATE_ERICSSON, 0) * 0.78)",
                        "SDCCH_TRAFFIC_NETWORK": "(HUAWEI_2G_KPI.SDCCH_TRAFFIC_HUAWEI) + (ERICSSON_2G_KPI.SDCCH_TRAFFIC_ERICSSON)",
                        "CELL_AVAILABILITY_RATE_NETWORK": "(COALESCE(HUAWEI_2G_KPI.CELL_AVAILABILITY_RATE_HUAWEI, 0) * 0.22) + (COALESCE(ERICSSON_2G_KPI.CELL_AVAILABILITY_RATE_ERICSSON, 0) * 0.78)"
                    },

                    "chart_configs": {
                        "CSSR_ALL": {
                            "KPIS": ["CSSR_NETWORK", "CSSR_HUAWEI", "CSSR_ERICSSON"],
                            "title": "2G CSSR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CSSR (%)",
                            "threshold": 99
                        },
                        "CDR_ALL": {
                            "KPIS": ["CDR_NETWORK", "CDR_HUAWEI", "CDR_ERICSSON"],
                            "title": "2G CDR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CDR (%)"
                        },
                        "CBR_ALL": {
                            "KPIS": ["CBR_NETWORK", "CBR_HUAWEI", "CBR_ERICSSON"],
                            "title": "2G CBR - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "CBR (%)",
                            "threshold": 3
                        },
                        "TCH_CONGESTION_RATE_ALL": {
                            "KPIS": ["TCH_CONGESTION_RATE_NETWORK", "TCH_CONGESTION_RATE_HUAWEI", "TCH_CONGESTION_RATE_ERICSSON"],
                            "title": "2G TCH Congestion - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "TCH Congestion (%)",
                            "threshold": 2
                        },
                        "SDCCH_CONGESTION_RATE_ALL": {
                            "KPIS": ["SDCCH_CONGESTION_RATE_NETWORK", "SDCCH_CONGESTION_RATE_HUAWEI", "SDCCH_CONGESTION_RATE_ERICSSON"],
                            "title": "2G SDCCH Congestion - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Congestion (%)",
                            "threshold": 1
                        },
                        "SDCCH_DROP_RATE_ALL": {
                            "KPIS": ["SDCCH_DROP_RATE_NETWORK", "SDCCH_DROP_RATE_HUAWEI", "SDCCH_DROP_RATE_ERICSSON"],
                            "title": "2G SDCCH Drop Rate - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Drop Rate (%)"
                        },
                        "CELL_AVAILABILITY_ALL": {
                            "KPIS": ["CELL_AVAILABILITY_RATE_NETWORK", "CELL_AVAILABILITY_RATE_HUAWEI", "CELL_AVAILABILITY_RATE_ERICSSON"],
                            "title": "2G Cell Availability - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "Availability (%)",
                            "threshold": 99
                        },
                        "SDCCH_TRAFFIC_ALL": {
                            "KPIS": ["SDCCH_TRAFFIC_NETWORK", "SDCCH_TRAFFIC_HUAWEI", "SDCCH_TRAFFIC_ERICSSON"],
                            "title": "2G SDCCH Traffic - Network & Vendors",
                            "default_type": "line",
                            "y_axis_title": "SDCCH Traffic (Erl)"
                        },

                        "CSSR_NETWORK_vs_CDR": {
                            "KPIS": ["CSSR_NETWORK", "CDR_NETWORK"],
                            "title": "2G Network CSSR vs CDR",
                            "default_type_1": "line",
                            "default_type_2": "bar",
                            "is_dual_axis": True,
                            "y_axis_titles": ["CSSR (%)", "CDR (%)"]
                        }

                    },

                    "sql_template": """
                        SELECT {fields}
                        FROM {cte_joins}
                        {group_by}
                        {order_by}
                    """
                },

        

            }
            ,

                "KPI_MONITORING2": {
                    "description": "2G HUAWEI KPI Monitoring",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],
                    "parameters": [],
                    "aggregation_levels": {
                    
                    },

                    "time_granularities": {
                        "HOURLY": {"is_available": True, "date_field":{"eric" "e.DATE"}, 
                                "time_field":{"e_time": "TIME_FORMAT(TIME, '%H:%i:%s') Time" } },

                        "DAILY": {"is_available": True, "date_field": "DATE", "time_field": None},
                        "WEEKLY": {"is_available": True, "date_field": "YEARWEEK(DATE, 1)", "time_field": None},
                        "MONTHLY": {"is_available": True, "date_field": "DATE_FORMAT(DATE, '%Y-%m')", "time_field": None}
                    },

                    # "kpi_fields": {
                    #      "CSSR_HUAWEI": """100 * (SUM(Suc_SDCCH_Seiz) / NULLIF(SUM(SDCCH_Seiz_Req), 0)) *
                    #         (1 - (SUM(SDCCHDrop) / NULLIF(SUM(Suc_SDCCH_Seiz), 0))) *
                    #         (SUM(Suc_TCH_Seiz_SG) + SUM(Suc_TCH_Seiz_TrafChann) + SUM(Suc_TCH_Seiz_handTrafChan)) /
                    #         NULLIF((SUM(TCH_Seizure_Req_SC) + SUM(TCH_Seiz_Req_TrafChan) + SUM(TCH_Seiz_Req_HandTrafChan)), 0) *
                    #         (1 - (SUM(TCHDrop_Nume_ARCEP) / NULLIF(SUM(TCHDrop_Deno_ARCEP), 0)))""",

                    #     "CDR_HUAWEI": "(100 * SUM(TCHDrop_Nume_ARCEP) / NULLIF(SUM(TCHDrop_Deno_ARCEP), 0))",
                    #     "CBR_HUAWEI": "100 * (SUM(TCHCONG_Nume_ARCEP) / NULLIF(SUM(TCHCONG_Deno_ARCEP), 0))"
                    # },

                    "chart_configs":{
                        
                        "CSSR_HUAWEI":{
                            "KPIS":['CSSR_HUAWEI'],
                            "title":"2G Huawei CSSR ",
                            "default_type": "line",
                            "y_axis_title":"CSSR (%)",
                            "threshold":99
                        },
                        "CSSR_CDR_HUAWEI":{
                            "KPIS":["CSSR_HUAWEI","CDR_HUAWEI"],
                            "title":"2G Huawei CSSR vs CDR",
                            "default_type_1": "line",
                            "default_type_2": "bar",
                            "is_dual_axis":True,
                            "y_axis_titles":["CSSR (%)", "CDR (%)"]
                        },
                        "CBR_HUAWEI":{
                            "KPIS":["CBR_HUAWEI"],
                            "title":"2G Huawei CBR ",
                            "default_type": "line",
                            "y_axis_title":"CBR (%)",
                            "threshold":3
                        }

                    },

                    "sql_template": """

                                        WITH
                        HUAWEI_2G_KPI AS (
                            SELECT
                            h.date,
                            h.time
                            -- h.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT,

                            
                            -- CASE
                            --   WHEN COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0) = 0
                            --     OR COALESCE(SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE)), 0) = 0
                            --     OR (COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0)) = 0
                            --     OR (COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                            --          + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)) = 0
                            --   THEN 0
                            --   ELSE
                            --     100.0
                            --     * (SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))
                            --         / SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)))
                            --     * (1.0 - (SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE))
                            --                / SUM(CAST(CELL_KPI_SD_SUCC AS DOUBLE))))
                            --     * ((SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                            --          + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                            --          + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))
                            --         / (SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE))
                            --             + SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE))
                            --             + SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE))))
                            --     * (1.0 - ((SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE))
                            --                 + SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE))
                            --                 + SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)))
                            --                / (SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE))
                            --                    + SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE))
                            --                    + SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)))))
                            -- END AS CSSR_HUAWEI
                            

                            ,100 * (SUM(CELL_KPI_SD_SUCC
                            ) / SUM(CELL_KPI_SD_REQ)) * 
                        (1 - (SUM(CELL_SD_CALL_DROPS) / SUM(CELL_KPI_SD_SUCC))) * 
                        (SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)) /
                        (SUM(CELL_KPI_TCH_REQ_SIG) + SUM(CELL_KPI_TCH_ASS_REQ_TRAF) + SUM(CELL_KPI_TCH_HO_REQ_TRAF)) *
                        (1 - (((sum(CELL_KPI_TCH_DROPS_SIG)+sum(CELL_KPI_TCH_STATIC_DROPS_TRAF)+sum(CELL_KPI_TCH_HO_DROPS_TRAF))) /
                            ((sum(CELL_KPI_TCH_SUCC_SIG)+sum(CELL_KPI_TCH_ASS_SUCC_TRAF)+sum(CELL_KPI_TCH_HO_SUCC_TRAF))))) AS  CSSR_HUAWEI,

                            -- ARCEP 2G CALL DROP RATE - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0),
                                0
                            ) AS CDR_HUAWEI,

                            -- ARCEP 2G CALL BLOCKING RATE - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_CONG_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS CBR_HUAWEI,

                            -- TCH Congestion Rate - HUAWEI
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS TCH_CONGESTION_RATE_HUAWEI,

                            -- SDCCH Congestion Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_KPI_SD_CONGEST AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_HUAWEI,

                            -- SDCCH Drop Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_IMM_ASS_SUCC_SD AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_HUAWEI,

                            -- ARCEP TCH Assignment Success Rate - HUAWEI (Vendor-specific)
                            100.0 * (
                                COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
                            ) / NULLIF(
                                COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
                                + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
                                0
                            ) AS TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,

                            -- SDCCH Traffic (Erlangs) - HUAWEI
                            COALESCE(SUM(CAST(CELL_KPI_SD_TRAF_ERL AS DOUBLE)), 0) AS SDCCH_TRAFFIC_HUAWEI,

                            -- 2G Availability Rate - HUAWEI
                            100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
                                NULLIF(COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0), 0) AS CELL_AVAILABILITY_RATE_HUAWEI,


                                COALESCE(SUM(CAST(CELL_KPI_TCH_TRAF_ERL_TRAF AS DOUBLE)), 0) TRAFFIC_VOIX_HUAWEI,
                                -- handover sr
                                100.0 * (
                        (COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_SUCC AS DOUBLE)), 0)
                        + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_SUCC AS DOUBLE)), 0))
                        / NULLIF(
                            COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_CMD AS DOUBLE)), 0)
                            + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_CMD AS DOUBLE)), 0),
                            0
                            )
                        ) AS HANDOVER_SUCCESS_RATE_HUAWEI



                            FROM
                            hourly_huawei_2g_all_counters h
                            -- LEFT JOIN
                            --   EPT_2G ept ON h.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'

                            WHERE
                            h.date BETWEEN '2026-01-26' AND '2026-01-26'  -- Adjust date range as needed

                            GROUP BY
                            h.date,
                            h.time
                            -- h.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT
                        ),

                        ERICSSON_2G_KPI AS (
                            SELECT
                            e.DATE,
                            e.TIME,
                            -- e.CELL_NAME,
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
                            COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) TRAFFIC_VOIX_ERICSSON
                            FROM
                            hourly_ericsson_arcep_2g_counters e
                            -- LEFT JOIN
                            --   EPT_2G ept ON e.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'

                            WHERE
                            e.DATE BETWEEN '2026-01-28' AND '2026-01-29'  -- Adjust date range as needed

                            GROUP BY
                            e.DATE,
                            e.TIME
                            -- e.CELL_NAME,
                            -- ept.SITE_NAME,
                            -- ept.ARRONDISSEMENT,
                            -- ept.COMMUNE,
                            -- ept.DEPARTEMENT
                        )



                        

                        SELECT
                        COALESCE(h.date, e.DATE) AS date,
                        COALESCE(h.time, e.TIME) AS time,

                        -- Location Info
                        -- COALESCE(h.SITE_NAME, e.SITE_NAME) AS SITE_NAME,
                        -- COALESCE(h.ARRONDISSEMENT, e.ARRONDISSEMENT) AS ARRONDISSEMENT,
                        -- COALESCE(h.COMMUNE, e.COMMUNE) AS COMMUNE,
                        -- COALESCE(h.DEPARTEMENT, e.DEPARTEMENT) AS DEPARTEMENT,

                        -- Vendor-specific KPIs
                        h.CSSR_HUAWEI,
                        -- h.CSSR_HUAWEI_2,
                        e.CSSR_ERICSSON,
                        h.CDR_HUAWEI,
                        e.CDR_ERICSSON,
                        h.CBR_HUAWEI,
                        e.CBR_ERICSSON,
                        h.TCH_CONGESTION_RATE_HUAWEI,
                        e.TCH_CONGESTION_RATE_ERICSSON,
                        h.SDCCH_CONGESTION_RATE_HUAWEI,
                        e.SDCCH_CONGESTION_RATE_ERICSSON,
                        h.SDCCH_DROP_RATE_HUAWEI,
                        e.SDCCH_DROP_RATE_ERICSSON,
                        h.SDCCH_TRAFFIC_HUAWEI,
                        e.SDCCH_TRAFFIC_ERICSSON,
                        h.CELL_AVAILABILITY_RATE_HUAWEI,
                        e.CELL_AVAILABILITY_RATE_ERICSSON,

                        h.TRAFFIC_VOIX_HUAWEI,
                        e.TRAFFIC_VOIX_ERICSSON,

                        -- Vendor-specific only
                        h.TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,
                        e.TCH_AVAILABILITY_RATE_ERICSSON,
                        e.DOWNTIME_MANUAL,
                        e.SDCCH_BLOCKING_RATE_ERICSSON,

                        h.HANDOVER_SUCCESS_RATE_HUAWEI,

                        -- Network-level weighted averages (0.22 Huawei + 0.78 Ericsson)
                        (COALESCE(h.CSSR_HUAWEI, 0) * 0.22) + (COALESCE(e.CSSR_ERICSSON, 0) * 0.78) AS CSSR_NETWORK,
                        (COALESCE(h.CDR_HUAWEI, 0) * 0.22) + (COALESCE(e.CDR_ERICSSON, 0) * 0.78) AS CDR_NETWORK,
                        (COALESCE(h.CBR_HUAWEI, 0) * 0.22) + (COALESCE(e.CBR_ERICSSON, 0) * 0.78) AS CBR_NETWORK,
                        (COALESCE(h.TCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.TCH_CONGESTION_RATE_ERICSSON, 0) * 0.78) AS TCH_CONGESTION_RATE_NETWORK,
                        (COALESCE(h.SDCCH_CONGESTION_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.SDCCH_CONGESTION_RATE_ERICSSON, 0) * 0.78) AS SDCCH_CONGESTION_RATE_NETWORK,
                        (COALESCE(h.SDCCH_DROP_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.SDCCH_DROP_RATE_ERICSSON, 0) * 0.78) AS SDCCH_DROP_RATE_NETWORK,
                        (COALESCE(h.SDCCH_TRAFFIC_HUAWEI, 0) * 0.22) + (COALESCE(e.SDCCH_TRAFFIC_ERICSSON, 0) * 0.78) AS SDCCH_TRAFFIC_NETWORK,
                        (COALESCE(h.CELL_AVAILABILITY_RATE_HUAWEI, 0) * 0.22) + (COALESCE(e.CELL_AVAILABILITY_RATE_ERICSSON, 0) * 0.78) AS CELL_AVAILABILITY_RATE_NETWORK,
                        h.TRAFFIC_VOIX_HUAWEI + e.TRAFFIC_VOIX_ERICSSON AS TRAFFIC_NETWORK

                        FROM HUAWEI_2G_KPI h
                        LEFT JOIN ERICSSON_2G_KPI e
                        ON h.date = e.DATE
                        AND h.time = e.TIME

                        ORDER BY date, time


                    """
                }


        },

        # =========================================================================
        # SAMPLE RAW_SQL QUERY (for testing the new query type)
        # =========================================================================
        "TEST_RAW_SQL": {

            "SAMPLE": {
                "KPI_TEST": {
                    "query_type": "raw_sql",
                    "description": "Sample raw_sql query - 2G Network KPIs",
                    "date_time_filters": ["start_date", "end_date", "multiple_date", "start_hour", "end_hour", "multiple_hour"],

                    "time_granularities": {
                        "HOURLY": {"is_available": True},
                        "DAILY": {"is_available": True},
                        "WEEKLY": {"is_available": True},
                        "MONTHLY": {"is_available": True}
                    },

                    "sources": {
                        "eric": {
                            "date_col": "e.DATE",
                            "time_col": "e.TIME",
                            "aggregations": {
                                "cell_name": "e.CELL_NAME",
                                "site_name": "e.SITE_NAME",
                                "commune": "e.COMMUNE"
                            }
                        },
                        "huawei": {
                            "date_col": "h.date",
                            "time_col": "h.time",
                            "aggregations": {
                                "cell_name": "h.cell_name",
                                "site_name": "h.site_name",
                                "commune": "h.COMMUNE"
                            }
                        }
                    },

                    # Joins config: auto-generate JOIN ON conditions based on granularity/aggregation
                    "joins": [
                        {
                            "left": "eric",
                            "right": "huawei",
                            "include_date": True,       # Always include date
                            "include_time": True,       # Only if HOURLY granularity
                            "include_aggregation": True, # Only if aggregation is selected
                            "custom": []                 # Extra static conditions if needed
                        }
                    ],

                    "sql_template": """
                        WITH ERICSSON_2G AS (
                            SELECT
                                {eric__select_fields},
                                SUM(e.counter1) AS kpi_eric_1,
                                SUM(e.counter2) AS kpi_eric_2
                            FROM ericsson_2g_table e
                            WHERE {eric__where_clause}
                            GROUP BY {eric__group_by}
                        ),
                        HUAWEI_2G AS (
                            SELECT
                                {huawei__select_fields},
                                SUM(h.counter1) AS kpi_huawei_1,
                                SUM(h.counter2) AS kpi_huawei_2
                            FROM huawei_2g_table h
                            WHERE {huawei__where_clause}
                            GROUP BY {huawei__group_by}
                        )
                        SELECT
                            COALESCE(e.date, h.date) AS date,
                            COALESCE(e.time, h.time) AS time,
                            e.kpi_eric_1,
                            e.kpi_eric_2,
                            h.kpi_huawei_1,
                            h.kpi_huawei_2,
                            (COALESCE(e.kpi_eric_1, 0) * 0.78) + (COALESCE(h.kpi_huawei_1, 0) * 0.22) AS kpi_network_1
                        FROM ERICSSON_2G e
                        LEFT JOIN HUAWEI_2G h
                            ON {eric__huawei__join_on}
                        ORDER BY {eric__order_by}
                    """
                }
            }

        }

}
