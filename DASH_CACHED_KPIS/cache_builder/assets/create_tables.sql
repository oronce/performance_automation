-- MySQL table : hourly_huawei_4g_packet_loss
-- auto_detect=False | varchar_to_decimal=True
CREATE TABLE IF NOT EXISTS hourly_huawei_4g_packet_loss (
    date                                     DATE  NOT NULL,
    time                                     TIME  NOT NULL,
    SITE_NAME                                VARCHAR  NULL,
    CELL_NAME                                VARCHAR  NOT NULL,
    eNodeB_ID                                VARCHAR  NULL,
    local_cell_id                            VARCHAR  NULL,
    L_Traffic_DL_PktUuLoss_Loss              DECIMAL(38, 12)  NULL,
    L_Traffic_DL_PktUuLoss_Tot               DECIMAL(38, 12)  NULL,
    L_Traffic_UL_PktLoss_Loss                DECIMAL(38, 12)  NULL,
    L_Traffic_UL_PktLoss_Tot                 DECIMAL(38, 12)  NULL,
    PRIMARY KEY (date, time, CELL_NAME)
);

-- --------------- MySQL table : hourly_huawei_3g_packet_loss
-- --------------- auto_detect=False | varchar_to_decimal=True
CREATE TABLE IF NOT EXISTS hourly_huawei_3g_packet_loss (
    date                                     DATE  NOT NULL,
    time                                     TIME  NOT NULL,
    controller_name                          VARCHAR  NOT NULL,
    adjacent_node_id                         VARCHAR  NOT NULL,
    phb                                      VARCHAR  NOT NULL,
    local_ip                                 VARCHAR  NULL,
    peer_ip                                  VARCHAR  NULL,
    VS_IPPOOL_IPPM_Local_TxPkts              DECIMAL(38, 12)  NULL,
    VS_IPPOOL_IPPM_Peer_RxPkts               DECIMAL(38, 12)  NULL,
    VS_IPPOOL_IPPM_Forward_DropMeans         DECIMAL(38, 12)  NULL,
    PRIMARY KEY (date, time, controller_name, adjacent_node_id, phb)
);

-- ------------------ MySQL table : huawei_adjacent_node_id_3g
-- --------------- auto_detect=True  : all VARCHAR, real types inferred on load
CREATE TABLE IF NOT EXISTS huawei_adjacent_node_id_3g (
    adjacent_node_id                         VARCHAR  NOT NULL,
    rnc_adjnode                              VARCHAR  NOT NULL,
    adjacent_node_name                       VARCHAR  NOT NULL,
    site_name                                VARCHAR  NOT NULL,
    rnc                                      VARCHAR  NOT NULL,
    PRIMARY KEY (adjacent_node_id, adjacent_node_name, rnc)
);
