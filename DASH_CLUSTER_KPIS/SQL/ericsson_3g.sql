SELECT
    DATE AS date{time_select},

    -- CS_CSSR (Circuit-Switched Call Setup Success Rate)
    100.0 *
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

    COALESCE(SUM(CAST(TRAFFIC_VOIX AS DOUBLE)), 0) AS TRAFFIC_VOIX,
    COALESCE(SUM(CAST(TRAFFIC_DATA_GB AS DOUBLE)), 0) AS TRAFFIC_DATA_GB

FROM
    hourly_ericsson_arcep_3g_counters

WHERE
    {date_filter}
    {cell_filter}

GROUP BY
    DATE{time_group}

ORDER BY
    DATE{time_group}
