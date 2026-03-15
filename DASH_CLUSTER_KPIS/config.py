# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DB_CONFIG = {
    'host': '10.22.33.116',
    'user': 'root',
    'password': 'performance',
    'database': 'performanceroute'
}

# =============================================================================
# DATE LIMITS
# =============================================================================
MAX_DAYS_ALLOWED = 30
MAX_SPECIFIC_DATES = 10   # max individual dates in specific-dates mode
MAX_COMPARE_DAYS = 7      # max days in compare mode
DEFAULT_DAYS = 2

# =============================================================================
# KPI CHART GROUPS
# Single series per chart (Huawei 2G cluster view)
# =============================================================================
KPI_CHART_GROUPS = {
    "CSSR (%)": {
        "columns": ["CSSR_HUAWEI"],
        "threshold": 99
    },
    "CDR (%)": {
        "columns": ["CDR_HUAWEI"],
        "threshold": 2
    },
    "CBR (%)": {
        "columns": ["CBR_HUAWEI"],
        "threshold": 1
    },
    "TCH Congestion Rate (%)": {
        "columns": ["TCH_CONGESTION_RATE_HUAWEI"],
        "threshold": None
    },
    "SDCCH Congestion Rate (%)": {
        "columns": ["SDCCH_CONGESTION_RATE_HUAWEI"],
        "threshold": None
    },
    "SDCCH Drop Rate (%)": {
        "columns": ["SDCCH_DROP_RATE_HUAWEI"],
        "threshold": None
    },
    "TCH Assignment Success Rate (%)": {
        "columns": ["TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI"],
        "threshold": None
    },
    "SDCCH Traffic (Erlang)": {
        "columns": ["SDCCH_TRAFFIC_HUAWEI"],
        "threshold": None
    },
    "Cell Availability Rate (%)": {
        "columns": ["CELL_AVAILABILITY_RATE_HUAWEI"],
        "threshold": 99
    },
    "Traffic Voice (Erlang)": {
        "columns": ["TRAFFIC_VOIX_HUAWEI"],
        "threshold": None
    },
    "Handover Success Rate (%)": {
        "columns": ["HANDOVER_SUCCESS_RATE_HUAWEI"],
        "threshold": None
    }
}

# =============================================================================
# CHART COLORS  (one color per KPI series)
# =============================================================================
CHART_COLORS = [
    "#e74c3c",  # Red
    "#3498db",  # Blue
    "#2ecc71",  # Green
    "#f39c12",  # Orange
    "#9b59b6",  # Purple
]

# =============================================================================
# CELL BATCHES
# =============================================================================
BATCH_1_CELL_NAME = [
  'BAGOU1','BAGOU2','BAGOU3','BASSO1','BEROU1','BEROU2','BEROU3','BIRLA1','BIRLA2','BOROD1','BOROD2','BOROD3','BRIGN2','DBAGOU1','DBAGOU3','DGOGOU1','DGOGOU2','DONWA1','DONWA2','DONWA3','DPEHUN3','DSEKER2','DSEKER3','FOBOU3','GAMIA1','GARAG2','GBASS1','GBASS2','GBASS3','GBEMO1','GBEMO2','GNAMB3','GNEMA2','GOGO21','GOGO22','GOGOU1','GOGOU2','GOGOU3','GOUMO1','GUESSB1','GUESSB3','KABO1','KABO2','KABO3','KAND21','KAND22','KAND23','KAND31','KAND33','KAND53','KANDI3','KANWO1','KARIM3','KASSA3','KERO33','KEROU3','KOROD1','KOSSO1','KOSSO2','KOSSO3','KOUTA1','KOUTA2','KOUTA3','LIBAN1','LIBAN2','LIBAN3','MAASS1','MAASS2','MALA41','MALAN1','OUARA1','OUARA2','OUARA3','OUSON1','PAR291','PAR292','PAR293','PEHUN1','PEHUN2','PEHUN3','PETIT1','PETIT2','PETIT3','PIAMI3','SAORE1','SEGBA1','SEGBA2','SEKER2','SEKER3','SIKKI1','SIKKI2','SIKKI3','SINEN1','SINEN2','SINEN3','SOKOT2','SORI1','SORI2','SORI3','SOUNO1','TCHAO2','TCHIC1','TCHIC2','TOBRE1','WARI1','YAMPO2','ZOUGO1','ZOUGO2','ZOUGO3'
]

BATCH_2_CELL_NAME = ['KAND53','GOROG1','KASSA3','PAR291','LIBAN3','GBEMO2','PAR292','SORI2','BOROD1','SORI1','SORI3','PAR293','DONWA2','KAND21','OUARA2','BASSO1','OUARA1','SOKOT2','PETIT1','KAND22','GOGOU3','OUARA3','BEROU2','BAGOU3','BEROU1','BEROU3','BOROD3','GOGO22','BAGOU2','SEKER3','BAGOU1','BOROD2','GOGOU1','KAND33','ZOUGO2','SEGBA1','SINEN3','SINEN2','PETIT2','KOUTA2','ZOUGO1','KOSSO3','WARI1','GOGOU2','DBAGOU3','SINEN1','KABO3','KANWO1','GUESSB1','KANDI3','SEGBA2','PEHUN1','KAND43','PETIT3','ZOUGO3','PEHUN2','SEKER2','GARAG2','KOROD1','MAASS1','DSEKER2','OUSON1','GBEMO1','LIBAN1','SEKER1','DBAGOU1','KOSSO2','TOBRE1','DGOGOU2','KOUTA3','GBASS2','PAR511','YAMPO2','DSEKER3','KIKAES3','GNAMB3','DGOGOU1','SIKKI1','KAND93','KAND23','PEHUN3','GAMIA1','GUESSB3','SAORE1','KABO1','KAND31','KAND92','GOGO21','SIKKI2','KABO2','PAR313','FOBOU3','SAORE2','SIKKI3','GOGO23','GNEMA3','SAKAB1','DPEHUN3','GNEMA2','DONWA3','KEROU3','GUESSB2','GBASS3','DPEHUN1','GBASS1','GNEMA1','FOBOU2','LIBAN2','MALA41','SAORE3','PAR512','TOBRE2','DGOGOU3','TOBRE3','KOUTA1','BORI2','DSEKER1','BRIGN2','BERKO1','SOUBO1','FOBOU1','PAR513','GAMIA2','TCHAO2','DPEHUN2','DIADI3','PAR423','GUESS3','THYA1','KPEBO2','GOMME1','GANRU1','TCHAO1','KAKOU1','TCHIC1','BANIT3','PAR422','BODJE3','GOUMO1','BOUKA2','DONWA1','PAR122','DGAMIA1','KAKIK1','TCHA22','KOMIG3','BOUKA1','PAR462','KIKAES2','KERO33','PAR311','BOUAN2','GBEI1','BORI1','KAND82','SANDI1','BEMBE1','KOMIG1','PAR501','DOUGO1'
]

BATCHES = {
    "batch1": BATCH_1_CELL_NAME,
    "batch2": BATCH_2_CELL_NAME,
}
