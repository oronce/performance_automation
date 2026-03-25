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
MAX_DAYS_ALLOWED    = 30
MAX_SPECIFIC_DATES  = 10   # max individual dates in specific-dates mode
MAX_COMPARE_DAYS    = 7    # max days in compare mode
DEFAULT_DAYS        = 2

# =============================================================================
# CHART COLORS  (shared across all technologies and vendors)
# =============================================================================
CHART_COLORS = [
    "#3498db",  # Blue
    "#2ecc71",  # Green
    "#f39c12",  # Orange
    "#9b59b6",  # Purple
    "#1abc9c",  # Teal
]

# =============================================================================
# CELL LISTS
# =============================================================================

# --- Huawei 2G ---
_HUAWEI_2G_CLUSTER_1 = [
    'BAGOU1','BAGOU2','BAGOU3','BASSO1','BEROU1','BEROU2','BEROU3','BIRLA1',
    'BIRLA2','BOROD1','BOROD2','BOROD3','BRIGN2','DBAGOU1','DBAGOU3','DGOGOU1',
    'DGOGOU2','DONWA1','DONWA2','DONWA3','DPEHUN3','DSEKER2','DSEKER3','FOBOU3',
    'GAMIA1','GARAG2','GBASS1','GBASS2','GBASS3','GBEMO1','GBEMO2','GNAMB3','GNEMA2',
    'GOGO21','GOGO22','GOGOU1','GOGOU2','GOGOU3','GOUMO1','GUESSB1','GUESSB3','KABO1',
    'KABO2','KABO3','KAND21','KAND22','KAND23','KAND31','KAND33','KAND53','KANDI3',
    'KANWO1','KARIM3','KASSA3','KERO33','KEROU3','KOROD1','KOSSO1','KOSSO2','KOSSO3',
    'KOUTA1','KOUTA2','KOUTA3','LIBAN1','LIBAN2','LIBAN3','MAASS1','MAASS2','MALA41',
    'MALAN1','OUARA1','OUARA2','OUARA3','OUSON1','PAR291','PAR292','PAR293','PEHUN1',
    'PEHUN2','PEHUN3','PETIT1','PETIT2','PETIT3','PIAMI3','SAORE1','SEGBA1','SEGBA2',
    'SEKER2','SEKER3','SIKKI1','SIKKI2','SIKKI3','SINEN1','SINEN2','SINEN3','SOKOT2',
    'SORI1','SORI2','SORI3','SOUNO1','TCHAO2','TCHIC1','TCHIC2','TOBRE1','WARI1',
    'YAMPO2','ZOUGO1','ZOUGO2','ZOUGO3'
]

_HUAWEI_2G_CELL_29_MARCH = [
    'BASSO1','KOSSO3','KOUTA2','WARI1','GBASS2','GBASS1','KOSSO2','GBASS3','MALA41','GBEMO2','GOGO22','SINEN2','KABO3','PEHUN2','KABO2','KABO1','PAR293','GBEMO1','GNAMB3','PAR292','GUESSB1','PAR291','MAASS1','KEROU3','KOROD1','KOSSO1','YAMPO2','KAND53'
]

_ERICSSON_2G_10_MARS_1000Plus_Cell = [
    'ABOM21','ABOM22','ABOM23','ABOM41','ABOM42','ABOM43','ABOM61','ABOM62','ABOM63','ABOM91','ABOM92','ABOM93','ADAKP1','ADAKP2','ADAKP3','ADJAH1','ADJAH2','ADJAH3','ADJAO1','ADJAO2','ADJAO3','ADJAR1','ADJAR2','ADJAR3','ADJI1','ADJI2','ADJI3','ADJOH1','ADJOH2','ADJOH3','ADOH1','ADOH2','ADOH3','AFFAME1','AFFAME2','AFFAME3','AGAME1','AGAME2','AGAME3','AGAN1','AGAN2','AGAN3','AGASS1','AGASS2','AGASS3','AGBNO1','AGBNO2','AGBNO3','AGBOG1','AGBOG2','AGBOG3','AGBOK1','AGBOK2','AGBOK3','AGBOTA1','AGBOTA2','AGBOTA3','AGLAP1','AGLAP2','AGLAP3','AGONG1','AGONG2','AGONG3','AGONK1','AGONK2','AGONK3','AGOR21','AGOR22','AGOR23','AGOU21','AGOU22','AGOU23','AGOUA1','AGOUA2','AGOUA3','AGOUE1','AGOUE2','AGOUE3','AGOUNA1','AGOUNA2','AGOUNA3','AGUEG1','AGUEG2','AGUEG3','AHOZ21','AHOZ22','AHOZ23','AHOZO1','AHOZO2','AHOZO3','AITC21','AITC22','AITC23','AKAD21','AKAD22','AKAD23','AKAD31','AKAD32','AKAD33','AKAS21','AKAS22','AKAS23','AKAS51','AKAS52','AKAS53','AKAS61','AKAS62','AKAS63','AKASS1','AKASS2','AKASS3','AKIZA1','AKIZA2','AKIZA3','AKLAN1','AKLAN2','AKLAN3','AKODE1','AKODE2','AKODE3','AKOG21','AKOG22','AKOG23','ALAFI1','ALAFI2','ALAFI3','ALEDJ1','ALEDJ2','ALEDJ3','ALLA31','ALLA32','ALLA33','ALLAD1','ALLAD2','ALLAD21','ALLAD22','ALLAD23','ALLAD3','ANAN1','ANAN2','ANAN3','AORO1','AORO2','AORO3','APLAH1','APLAH2','APLAH3','ATCHO1','ATCHO2','ATCHO3','ATHIE1','ATHIE2','ATHIE3','ATOME1','ATOME2','ATOME3','ATRO21','ATRO22','ATRO23','ATRO31','ATRO32','ATRO33','ATTOGO1','ATTOGO2','ATTOGO3','AVAKP1','AVAKP2','AVAKP3','AVAM1','AVAM2','AVAM3','AYELA1','AYELA2','AYELA3','AYOM1','AYOM2','AYOM3','AYOU1','AYOU2','AYOU3','AZOHO1','AZOHO2','AZOHO3','AZOWL1','AZOWL2','AZOWL3','BANAME1','BANAME2','BANAME3','BANT21','BANT22','BANT23','BANTE1','BANTE2','BANTE3','BAREI1','BAREI2','BAREI3','BARIE1','BARIE2','BARIE3','BASSI1','BASSI2','BASSI3','BELL1','BELL2','BELL3','BEREC1','BEREC2','BEREC3','BETOUM1','BETOUM2','BETOUM3','BIRNI1','BIRNI2','BIRNI3','BOBE1','BOBE2','BOBE3','BODI1','BODI2','BODI3','BOH101','BOH102','BOH103','BOH131','BOH132','BOH133','BOH151','BOH152','BOH153','BOH161','BOH162','BOH163','BOHI111','BOHI112','BOHI113','BOHI31','BOHI32','BOHI33','BOHI91','BOHI92','BOHI93','BOHIC11','BOHIC12','BOHIC13','BONOU1','BONOU2','BONOU3','BOPA1','BOPA2','BOPA3','BOUGO1','BOUGO2','BOUGO3','BOUKO1','BOUKO2','BOUKO3','CAMPO1','CAMPO2','CAMPO3','CANA1','CANA2','CANA3','CASA1','CASA2','CASA3','CASSE1','CASSE2','CASSE3','CEB1','CEB2','CEB3','CENAG1','CENAG2','CENAG3','COBLI1','COBLI2','COBLI3','COCO11','COCO12','COCO13','COCOC1','COCOC2','COCOC3','COHOU1','COHOU2','COHOU3','COME1','COME2','COME3','COME31','COME32','COME33','COME41','COME42','COME43','COME51','COME52','COME53','COME71','COME72','COME73','COPAR1','COPAR2','COPAR3','COTIA1','COTIA2','COTIA3','COVE1','COVE2','COVE21','COVE22','COVE23','COVE3','DAGLAE1','DAGLAE2','DAGLAE3','DAGLAN1','DAGLAN2','DAGLAN3','DAGLAU1','DAGLAU2','DAGLAU3','DAGOUN1','DAGOUN2','DAKASS1','DAKASS2','DAKASS3','DAKODE1','DAKODE2','DALLA21','DALLA22','DALLAD1','DALLAD2','DALLAD3','DAN1','DAN2','DAN3','DANGB1','DANGB2','DANGB3','DANTO1','DANTO2','DANTO3','DASAR1','DASAR2','DASAR3','DASIL1','DASIL2','DASIL3','DASS11','DASS12','DASS13','DASS21','DASS22','DASS23','DASS31','DASS32','DASS33','DASS41','DASS42','DASS43','DATOR1','DATOR2','DATOR3','DATTOG1','DATTOG2','DATTOG3','DBETOU1','DBETOU2','DBOH111','DBOH112','DBOH113','DBOH151','DBOH152','DBOH153','DBOH161','DBOH162','DBOHI31','DBOHI32','DBOHI33','DBOHI91','DBOHI92','DBOHI93','DCOBLI2','DCOME21','DCOME52','DCOVE1','DCOVE2','DCOVE3','DDAN1','DDANT1','DDANT2','DDANT3','DDASS11','DDASS13','DDASS21','DDASS22','DDASS32','DDASS33','DDAVOZ1','DDAVOZ2','DDAVOZ3','DDJAKO1','DDJAKO2','DDJANG1','DDJANG2','DDJIDA2','DDJIDA3','DDJOU11','DDJOU12','DDJOU13','DDJOU22','DDJOU31','DDJOU32','DDJOU33','DDOGBO1','DDOGBO3','DDOKO1','DDOKO3','DEDOME1','DEDOME2','DEDOME3','DEGAU1','DEGAU2','DEGAU3','DEKOU1','DEKOU2','DEKOU3','DEKPO1','DEKPO2','DEKPO3','DENO1','DENO2','DENO3','DETOH1','DETOH2','DETOH3','DETOI1','DETOI2','DETOI3','DEVE1','DEVE2','DEVE3','DFIDJ11','DFIDJ12','DFIDJ13','DGLOD21','DGLOD22','DGLOD23','DGLODJ1','DGLODJ2','DGLODJ3','DGRAN23','DHOUEY3','DINDE1','DINDE2','DINDE3','DJABA1','DJABA2','DJABA3','DJAKO1','DJAKO2','DJAKO3','DJANE1','DJANE2','DJANE3','DJANG1','DJANG2','DJANG3','DJEFF1','DJEFF2','DJEFF3','DJEGB1','DJEGB2','DJEGB3','DJIDJ1','DJIDJ2','DJIDJ3','DJOH1','DJOH2','DJOH3','DJOT1','DJOT2','DJOT3','DJOU11','DJOU12','DJOU13','DJOU21','DJOU22','DJOU23','DJOU71','DJOU72','DJOU73','DJOU81','DJOU82','DJOU83','DJREG1','DJREG2','DJREG3','DKISSA1','DKISSA2','DKOUDO2','DKPADO1','DKPADO2','DKPADO3','DLOKO11','DLOKO12','DLOKO13','DLOKO21','DLOKO23','DLOKO41','DLOKO42','DLOKO43','DMBAR1','DMBAR2','DMBAR3','DNATI11','DNATI12','DNATI13','DOGB21','DOGB22','DOGB23','DOGBO1','DOGBO2','DOGBO3','DOKO1','DOKO2','DOKO3','DONA1','DONA2','DONA3','DOUAND1','DOUAND2','DOUAND3','DOUED21','DOUEDO1','DOWA1','DOWA2','DOWA3','DPATAR1','DSAVA32','DSAVA33','DSAVA41','DSAVA42','DSAVA43','DSAVAL1','DSAVAL2','DSE22','DSEGBO3','DSEHOU1','DSEME3','DSIMP13','DSITM11','DSITM12','DSITM13','DSITMO1','DSITMO2','DSITMO3','DSNOVI1','DSNOVI2','DSNOVI3','DSOCLO1','DSTOU1','DSTOU2','DSTOU3','DSUMA1','DSUMA2','DSUMA3','DTANGU1','DTANGU4','DTCHET1','DTOUI1','DTOUI2','DTOUI3','DTOVIK1','DWOLOG1','DWOLOG2','DZAGNA1','DZAGNA2','DZINVI1','DZINVI2','DZINVI3','DZOGBD2','EFFEO1','EFFEO2','EFFEO3','EKPE1','EKPE2','EKPE3','ETOI1','ETOI2','ETOI3','FAKA1','FAKA2','FAKA3','FIDJ21','FIDJ22','FIDJ23','FIFAD1','FIFAD2','FIFAD3','FIGNO1','FIGNO2','FIGNO3','FIROU1','FIROU2','FIROU3','GANH21','GANH22','GANH23','GANHI1','GANHI2','GANHI3','GAOUN1','GAOUN2','GAOUN3','GBADA1','GBADA2','GBADA3','GBANL1','GBANL2','GBANL3','GBEK1','GBEK2','GBEK3','GBETAG1','GBETAG2','GBETAG3','GBOZO1','GBOZO2','GBOZO3','GLAZ21','GLAZ22','GLAZ23','GLAZ31','GLAZ32','GLAZ33','GLOD21','GLOD22','GLOD23','GLOD31','GLOD32','GLOD33','GLODJ1','GLODJ2','GLODJ3','GOBAD1','GOBAD2','GOBAD3','GOBE1','GOBE2','GOBE3','GODO21','GODO22','GODO23','GODOG1','GODOG2','GODOG3','GODOM1','GODOM2','GODOM3','GOHOM1','GOHOM2','GOHOM3','GOUAN1','GOUAN2','GOUAN3','GOUKA1','GOUKA2','GOUKA3','GRAN21','GRAN22','GRAN23','GUILM1','GUILM2','GUILM3','HEKANM1','HEKANM2','HEKANM3','HEVI11','HEVI12','HEVI13','HEVI31','HEVI32','HEVI33','HEVI51','HEVI52','HEVI53','HEVIE21','HEVIE22','HEVIE23','HILAC1','HILAC2','HILAC3','HLAGB1','HLAGB2','HLAGB3','HLASS1','HLASS2','HLASS3','HLAZO1','HLAZO2','HLAZO3','HONVI1','HONVI2','HONVI3','HOUEY1','HOUEY2','HOUEY3','HOUN1','HOUN2','HOUN3','HOUNK1','HOUNK2','HOUNK3','IFANG1','IFANG2','IFANG3','IGBOD1','IGBOD2','IGBOD3','IGOLO1','IGOLO2','IGOLO3','IKPIN1','IKPIN2','IKPIN3','ITADJ1','ITADJ2','ITADJ3','IWOY1','IWOY2','IWOY3','JPII1','JPII2','JPII3','KABOU1','KABOU2','KABOU3','KALAV1','KALAV2','KALAV3','KANSO1','KANSO2','KANSO3','KAOBA1','KAOBA2','KAOBA3','KATAG1','KATAG2','KATAG3','KETO11','KETO12','KETO13','KETO21','KETO22','KETO23','KETO31','KETO32','KETO33','KISSA1','KISSA2','KISSA3','KLOUE1','KLOUE2','KLOUE3','KOKOR1','KOKOR2','KOKOR3','KOKOU1','KOKOU2','KOKOU3','KOLOK1','KOLOK2','KOLOK3','KOTOP1','KOTOP2','KOTOP3','KOUDO1','KOUDO2','KOUDO3','KOUNT1','KOUNT2','KOUNT3','KOUTY1','KOUTY3','KPANKO1','KPANKO2','KPANKO3','KPATA1','KPATA2','KPATA3','KPOMA1','KPOMA2','KPOMA3','KPOSE1','KPOSE2','KPOSE3','KPOTA1','KPOTA2','KPOTA3','KPOTO1','KPOTO2','KPOTO3','KRAKE1','KRAKE2','KRAKE3','LANT1','LANT2','LANT3','LENI21','LENI22','LENI23','LENIN1','LENIN2','LENIN3','LISSA1','LISSA2','LISSA3','LISSE1','LISSE2','LISSE3','LOBOG1','LOBOG2','LOBOG3','LOGOZ1','LOGOZ2','LOGOZ3','LOKO11','LOKO12','LOKO13','LOKO21','LOKO22','LOKO23','LOKO31','LOKO32','LOKO33','LOKO42','LOKOE1','LOKOE2','LOKOE3','LOKOG1','LOKOG2','LOKOG3','LOUWO1','LOUWO2','LOUWO3','MADJ1','MADJ2','MADJ3','MAKI21','MAKI22','MAKI23','MALAH1','MALAH2','MALAH3','MANIG1','MANIG2','MANIG3','MANSO1','MANSO2','MANSO3','MANTA1','MANTA2','MANTA3','MASSE1','MASSE2','MASSE3','MASSI1','MASSI2','MASSI3','MEDED1','MEDED2','MEDED3','MONK1','MONK2','MONK3','MOOVH1','MOOVH2','MOOVH3','MOUGNO1','MOUGNO2','MOUGNO3','NASSO1','NASSO2','NASSO3','NATI11','NATI12','NATI13','NATI21','NATI22','NATI23','NATI31','NATI32','NATI33','NATI41','NATI42','NATI43','NATI51','NATI52','NATI53','NATI61','NATI62','NATI63','NATI71','NATI72','NATI73','NDAHON1','NDAHON2','NDAHON3','ONIG21','ONIG22','ONIG23','ONIGBL1','ONIGBL2','ONIGBL3','ONKLO1','ONKLO2','ONKLO3','OROUK1','OROUK2','OROUK3','OTTO1','OTTO2','OTTO3','OUAKE1','OUAKE2','OUAKE3','OUEAD1','OUEAD2','OUEAD3','OUED21','OUED22','OUED23','OUEDE1','OUEDE2','OUEDE3','OUEDO1','OUEDO2','OUEDO3','OUEOE1','OUEOE2','OUEOE3','OUESS1','OUESS2','OUESS3','OUID11','OUID12','OUID13','OUID14','OUID21','OUID22','OUID23','OUINH1','OUINH2','OUINH3','OUOGH1','OUOGH2','OUOGH3','OWODE1','OWODE2','OWODE3','PAHO41','PAHO42','PAHO43','PAHO51','PAHO52','PAHO53','PAOUI1','PAOUI2','PAOUI3','PAPAR1','PAPAR2','PAPAR3','PARN11','PARN12','PARN13','PARN21','PARN22','PARN23','PATAR1','PATAR2','PATAR3','PELEB1','PELEB2','PELEB3','PENES1','PENES2','PENES3','PERMA1','PERMA2','PERMA3','PIRA1','PIRA2','PIRA3','PK31','PK32','PK33','PK91','PK92','PK93','POBE21','POBE22','POBE23','PORGA1','PORGA2','PORGA3','POSSO1','POSSO2','POSSO3','PREKE1','PREKE2','PREKE3','ROUDPE1','ROUDPE2','ROUDPE3','SACLO1','SACLO2','SACLO3','SAKET1','SAKET2','SAKET3','SAVA21','SAVA22','SAVA23','SAVA31','SAVAL1','SAVAL2','SAVAL3','SAVE21','SAVE22','SAVE23','SAVE31','SAVE32','SAVE33','SAVI1','SAVI2','SAVI3','SE21','SE22','SE23','SEDJED1','SEDJED2','SEDJED3','SEGBO1','SEGBO2','SEGBO3','SEHOU1','SEHOU2','SEHOU3','SEKAN1','SEKAN2','SEKAN3','SEME1','SEME2','SEME3','SEMER1','SEMER2','SEMER3','SETTO1','SETTO2','SETTO3','SEY11','SEY12','SEY13','SIKEC1','SIKEC2','SIKEC3','SOCLO1','SOCLO2','SOCLO3','SOKPO1','SOKPO2','SOKPO3','SOS1','SOS2','SOS3','SUCOB1','SUCOB2','SUCOB3','TAKON1','TAKON2','TAKON3','TANGU1','TANGU2','TANGU3','TANK21','TANK22','TANK23','TCHET1','TCHET2','TCHET3','TCHETO1','TCHETO2','TCHETO3','TCHIN1','TCHIN2','TCHIN3','TIND21','TIND22','TIND23','TOGB21','TOGB22','TOGB23','TOGBA1','TOGBA2','TOGBA3','TOGO11','TOGO12','TOGO13','TOGO21','TOGO22','TOGO23','TOHOUE1','TOHOUE2','TOHOUE3','TOKO1','TOKO2','TOKO3','TOKPD1','TOKPD2','TOKPD3','TONAT1','TONAT2','TONAT3','TORIB1','TORIB2','TORIB3','TORICA1','TORICA2','TORICA3','TOUCO1','TOUCO2','TOUCO3','TOUI1','TOUI2','TOUI3','TOVIK1','TOVIK2','TOVIK3','TOWE1','TOWE2','TOWE3','TRIPO1','TRIPO2','TRIPO3','VAKON2','VAKON3','VANH1','VANH2','VANH3','YAOUI1','YAOUI2','YAOUI3','YOKO1','YOKO2','YOKO3','ZAGNA1','ZAGNA2','ZAGNA3','ZAHLA1','ZAHLA2','ZAHLA3','ZAKPO1','ZAKPO2','ZAKPO3','ZALI1','ZALI2','ZALI3','ZE1','ZE2','ZE3','ZINVI1','ZINVI2','ZINVI3','ZOGB11','ZOGB12','ZOGB13','ZOGB21','ZOGB22','ZOGB23','ZOGB41','ZOGB42','ZOGB43','ZOGBD1','ZOGBD2','ZOGBD3','ZOGBO1','ZOGBO2','ZOGBO3','ZONG31','ZONG32','ZONG33','ZOUKO1','ZOUKO2','ZOUKO3','ZOUN1','ZOUN2','ZOUN3','ZOUNO1','ZOUNO2','ZOUNO3','ZOUZO1','ZOUZO2','ZOUZO3','HOUEY21','HOUEY22','HOUEY23','DODJB3','DODJB2','DODJB1','AGLOG3','AGLOG2','AGLOG1','HEHOU3','HEHOU2','HEHOU1','DJAVI3','DJAVI2','DJAVI1','AGAS23','AGAS22','AGAS21','GBEDJ3','GBEDJ2','GBEDJ1','DJEF23','DJEF22','DJEF21','VAKO23','VAKO22','VAKO21','WESTA3','HOUND1','WESTA1','HOUND3','HOUND2','WESTA2','ADOUK2','ADOUK1','ADOUK3','DJOU63','DJOU62','DJOU61','DJOU53','DJOU52','DJOU51','BASS23','BASS22','BASS21'
]

_ERICSSON_2G_LAC_TAC_CLUSTER_1 = [
    'AGLOG1','AGLOG2','AGLOG3','AGOUNA1','AGOUNA2','AGOUNA3','DAGOUN1','DAGOUN2',
    'AKOUN1','AKOUN2','AKOUN3','ALAFI1','ALAFI2','ALAFI3','BODJE1','BODJE2','BODJE3',
    'CANA1','CANA2','CANA3','COME1','COME2','COME3','COME21','COME22','COME23',
    'DCOME21','COME31','COME32','COME33','COME41','COME42','COME43','COME51','COME52',
    'COME53','DCOME52','COME61','COME62','COME63','COME71','COME72','COME73','COME81',
    'COME82','COME83','COME91','COME92','COME93','DDOGBO1','DDOGBO3','DOGBO1','DOGBO2',
    'DOGBO3','DOGB21','DOGB22','DOGB23','GOBAD1','GOBAD2','GOBAD3','GOGOR1','GOGOR2',
    'GOGOR3','HELOT1','HELOT2','HELOT3','HLAGB1','HLAGB2','HLAGB3','KABOU1','KABOU2',
    'KABOU3','DKANDI1','DKANDI2','DKANDI3','KANDI1','KANDI2','KANDI3','KASSOU1',
    'KASSOU2','KASSOU3','DKISSA1','DKISSA2','KISSA1','KISSA2','KISSA3','KOUMA1',
    'KOUMA3','KOUMA2','LOKO81','LOKO82','LOKO83','LOKO93','LOKO91','LOKO92','MALAN1',
    'MALAN2','MALAN3','DMALA21','DMALA22','DMALA23','MALA21','MALA22','MALA23','MALA31',
    'MALA32','MALA33','MALA41','MALA42','MALA43','MALA51','MALA52','MALA53','MALA61',
    'MALA62','MALA63','MALAH1','MALAH2','MALAH3','MASSI1','MASSI2','MASSI3','NAT121',
    'NAT122','NAT123','NATI51','NATI52','NATI53','NDAHON1','NDAHON2','NDAHON3','PAPAN1',
    'PAPAN2','PAPAN3','SOKPO1','SOKPO2','SOKPO3','SONTA1','SONTA2','SONTA3','TCHAO1',
    'TCHAO2','TCHAO3','TCHA21','TCHA22','TCHA23','THIO1','THIO2','THIO3','YAMBO1',
    'YAMBO2','YAMBO3','ZALI1','ZALI2','ZALI3'
]

_ERICSSON_3G_CLUSTER_1 = [
'UAGLOG7','UAGLOG8','UAGLOG9','UAGOUN7','UAGOUN8','UAGOUN9','UAKOUN7','UAKOUN8','UAKOUN9','UALAFI7','UALAFI8','UALAFI9','UBODJE7','UBODJE8','UBODJE9','UCANA7','UCANA8','UCANA9','UCOME7','UCOME8','UCOME9','UCOME27','UCOME28','UCOME29','UCOME37','UCOME38','UCOME39','UCOME47','UCOME48','UCOME49','UCOME57','UCOME58','UCOME59','UCOME67','UCOME68','UCOME69','UCOME77','UCOME78','UCOME79','UCOME87','UCOME88','UCOME89','UCOME97','UCOME98','UCOME99','UDOGBO7','UDOGBO8','UDOGBO9','UDOGB27','UDOGB28','UDOGB29','UGOBAD7','UGOBAD8','UGOBAD9','UGOGOR7','UGOGOR8','UGOGOR9','UHELOT7','UHELOT8','UHELOT9','UHLAGB7','UHLAGB8','UHLAGB9','UKABOU7','UKABOU8','UKABOU9','UKANDI7','UKANDI8','UKANDI9','UKASSO7','UKASSO8','UKASSO9','UKISSA7','UKISSA8','UKISSA9','UKOUMA7','UKOUMA8','UKOUMA9','ULOKO87','ULOKO88','ULOKO89','ULOKO97','ULOKO98','ULOKO99','UMALAN7','UMALAN8','UMALAN9','UMALA27','UMALA28','UMALA29','UMALA37','UMALA38','UMALA39','UMALA47','UMALA48','UMALA49','UMALA57','UMALA58','UMALA59','UMALA67','UMALA68','UMALA69','UMALAH7','UMALAH8','UMALAH9','UMASSI7','UMASSI8','UMASSI9','UNAT127','UNAT128','UNAT129','UNATI57','UNATI58','UNATI59','UNDAHO7','UNDAHO8','UNDAHO9','UPAPAN7','UPAPAN8','UPAPAN9','USOKPO7','USOKPO8','USOKPO9','USONTA7','USONTA8','USONTA9','UTCHAO7','UTCHAO8','UTCHAO9','UTCHA27','UTCHA28','UTCHA29','UTHIO7','UTHIO8','UTHIO9','UYAMBO7','UYAMBO8','UYAMBO9','UZALI17','UZALI18','UZALI19'
]

_ERICSSON_4G_CLUSTER_1 = [
'LAGLOGB1','LAGLOGB2','LAGLOGB3','LAGLOGB4','LAGLOGB5','LAGLOGB6','LAGOUN1','LAGOUN2','LAGOUN3','LAKOUN1','LAKOUN2','LAKOUN3','LALAFI1','LALAFI2','LALAFI3','LBODJE1','LBODJE2','LBODJE3','LBODJE4','LBODJE5','LBODJE6','LBODJE7','LBODJE8','LBODJE9','LCANA1','LCANA2','LCANA3','LCOME1','LCOME2','LCOME3','LCOME4','LCOME5','LCOME6','LCOME21','LCOME22','LCOME23','LCOME24','LCOME25','LCOME26','LCOME31','LCOME32','LCOME33','LCOME34','LCOME35','LCOME36','LCOME41','LCOME42','LCOME43','LCOME44','LCOME45','LCOME46','LCOME51','LCOME52','LCOME53','LCOME54','LCOME55','LCOME56','LCOME61','LCOME62','LCOME63','LCOME64','LCOME65','LCOME66','LCOME71','LCOME72','LCOME73','LCOME81','LCOME82','LCOME83','LCOME87','LCOME88','LCOME89','LCOME8A','LCOME8B','LCOME8C','LCOME91','LCOME92','LCOME93','LCOME94','LCOME95','LCOME96','LCOME97','LCOME98','LCOME99','LCOME9A','LCOME9B','LCOME9C','LDOGBO1','LDOGBO2','LDOGBO3','LDOGBO7','LDOGBO8','LDOGBO9','LDOGBOA','LDOGBOB','LDOGBOC','LDOGB21','LDOGB22','LDOGB23','LDOGB27','LDOGB28','LDOGB29','LDOGB2A','LDOGB2B','LDOGB2C','LGOBAD1','LGOBAD2','LGOBAD3','LGOGOR1','LGOGOR2','LGOGOR3','LHELOT1','LHELOT2','LHELOT3','LHLAGB1','LHLAGB2','LHLAGB3','LKABOU1','LKABOU2','LKABOU3','LKANDI1','LKANDI2','LKANDI3','LKANDI4','LKANDI5','LKANDI6','LKANDI7','LKANDI8','LKANDI9','LKANDIA','LKANDIB','LKANDIC','LKASSO1','LKASSO2','LKASSO3','LKASSO4','LKASSO5','LKASSO6','LKASSO7','LKASSO8','LKASSO9','LKISSA1','LKISSA2','LKISSA3','LKISSA7','LKISSA8','LKISSA9','LKISSAA','LKISSAB','LKISSAC','LKOUMA1','LKOUMA2','LKOUMA3','LKOUMA7','LKOUMA8','LKOUMA9','LLOKO81','LLOKO82','LLOKO83','LLOKO91','LLOKO92','LLOKO93','LLOKO94','LLOKO95','LLOKO96','LLOKO97','LLOKO98','LLOKO99','LLOKO9A','LLOKO9B','LLOKO9C','LMALAN1','LMALAN2','LMALAN3','LMALAN4','LMALAN5','LMALAN6','LMALAN7','LMALAN8','LMALAN9','LMALANA','LMALANB','LMALANC','LMALA21','LMALA22','LMALA23','LMALA24','LMALA25','LMALA26','LMALA87','LMALA88','LMALA89','LMALA2A','LMALA2B','LMALA2C','LMALA31','LMALA32','LMALA33','LMALA34','LMALA35','LMALA36','LMALA37','LMALA38','LMALA39','LMALA41','LMALA42','LMALA43','LMALA47','LMALA48','LMALA49','LMALA51','LMALA52','LMALA53','LMALA57','LMALA58','LMALA59','LMALA61','LMALA62','LMALA63','LMALA67','LMALA68','LMALA69','LMALAH1','LMALAH2','LMALAH3','LMASSI1','LMASSI2','LMASSI3','LNAT121','LNAT122','LNAT123','LNAT127','LNAT128','LNAT129','LNAT12A','LNAT12B','LNAT12C','LNATI51','LNATI52','LNATI53','LNATI54','LNATI55','LNATI56','LNDAHO1','LNDAHO2','LNDAHO3','LPAPAN1','LPAPAN2','LPAPAN3','LPAPAN4','LPAPAN5','LPAPAN6','LPAPAN7','LPAPAN8','LSOKPO1','LSOKPO2','LSOKPO3','LSONTA1','LSONTA2','LSONTA3','LTCHAO1','LTCHAO2','LTCHAO3','LTCHAO4','LTCHAO5','LTCHAO6','LTCHAO7','LTCHAO8','LTCHAO9','LTCHAOA','LTCHAOB','LTCHAOC','LTCHA21','LTCHA22','LTCHA23','LTCHA24','LTCHA25','LTCHA26','LTCHA87','LTCHA88','LTCHA89','LTCHA2A','LTCHA2B','LTCHA2C','LTHIO1','LTHIO2','LTHIO3','LYAMBO1','LYAMBO2','LYAMBO3','LZALI11','LZALI12','LZALI13'
]

_HUAWEI_2G_CLUSTER_2 = [
    'KAND53','GOROG1','KASSA3','PAR291','LIBAN3','GBEMO2','PAR292','SORI2','BOROD1',
    'SORI1','SORI3','PAR293','DONWA2','KAND21','OUARA2','BASSO1','OUARA1','SOKOT2',
    'PETIT1','KAND22','GOGOU3','OUARA3','BEROU2','BAGOU3','BEROU1','BEROU3','BOROD3',
    'GOGO22','BAGOU2','SEKER3','BAGOU1','BOROD2','GOGOU1','KAND33','ZOUGO2','SEGBA1',
    'SINEN3','SINEN2','PETIT2','KOUTA2','ZOUGO1','KOSSO3','WARI1','GOGOU2','DBAGOU3',
    'SINEN1','KABO3','KANWO1','GUESSB1','KANDI3','SEGBA2','PEHUN1','KAND43','PETIT3',
    'ZOUGO3','PEHUN2','SEKER2','GARAG2','KOROD1','MAASS1','DSEKER2','OUSON1','GBEMO1',
    'LIBAN1','SEKER1','DBAGOU1','KOSSO2','TOBRE1','DGOGOU2','KOUTA3','GBASS2','PAR511',
    'YAMPO2','DSEKER3','KIKAES3','GNAMB3','DGOGOU1','SIKKI1','KAND93','KAND23','PEHUN3',
    'GAMIA1','GUESSB3','SAORE1','KABO1','KAND31','KAND92','GOGO21','SIKKI2','KABO2',
    'PAR313','FOBOU3','SAORE2','SIKKI3','GOGO23','GNEMA3','SAKAB1','DPEHUN3','GNEMA2',
    'DONWA3','KEROU3','GUESSB2','GBASS3','DPEHUN1','GBASS1','GNEMA1','FOBOU2','LIBAN2',
    'MALA41','SAORE3','PAR512','TOBRE2','DGOGOU3','TOBRE3','KOUTA1','BORI2','DSEKER1',
    'BRIGN2','BERKO1','SOUBO1','FOBOU1','PAR513','GAMIA2','TCHAO2','DPEHUN2','DIADI3',
    'PAR423','GUESS3','THYA1','KPEBO2','GOMME1','GANRU1','TCHAO1','KAKOU1','TCHIC1',
    'BANIT3','PAR422','BODJE3','GOUMO1','BOUKA2','DONWA1','PAR122','DGAMIA1','KAKIK1',
    'TCHA22','KOMIG3','BOUKA1','PAR462','KIKAES2','KERO33','PAR311','BOUAN2','GBEI1',
    'BORI1','KAND82','SANDI1','BEMBE1','KOMIG1','PAR501','DOUGO1'
]

# --- Ericsson 2G ---
# Add batches when ready:
# _ERICSSON_2G_ZONE_NORTH = ['CELL1', ...]

# --- Ericsson 3G ---
# Add batches when ready:
# _ERICSSON_3G_ZONE_NORTH = ['CELL1', ...]

# --- Ericsson 4G ---
# Add batches when ready:
# _ERICSSON_4G_ZONE_NORTH = ['CELL1', ...]

# =============================================================================
# TECHNOLOGIES
#
# Structure:
#   TECHNOLOGIES[tech_key] = {
#       "label":   str,            # shown in the UI tab
#       "vendors": {
#           vendor_key: {
#               "label":    str,   # shown in vendor button
#               "sql_file": str,   # filename in SQL/ directory
#               "date_col": str,   # column ref used in WHERE date filter
#               "time_col": str,   # column ref injected for hourly select/group
#               "cell_col": str,   # column ref used in WHERE cell filter
#               "kpi_groups": {
#                   "Chart Title": {"columns": ["COL_ALIAS"], "threshold": N|None}
#               },
#               "batches": {
#                   "batch_key": {"label": "Display Name", "cells": [...]}
#               }
#           }
#       }
#   }
#
# Batch "all" is always added automatically — do NOT define it here.
# =============================================================================

TECHNOLOGIES = {

    # =========================================================================
    # 2G
    # =========================================================================
    "2g": {
        "label": "2G",
        "vendors": {

            # -----------------------------------------------------------------
            # Ericsson 2G
            # -----------------------------------------------------------------
            "ericsson": {
                "label"    : "Ericsson",
                "sql_file" : "ericsson_2g.sql",
                "date_col" : "e.DATE",
                "time_col" : "e.TIME",
                "cell_col" : "e.CELL_NAME",

                "kpi_groups": {
                    "2G CSSR (%)": {
                        "columns": ["CSSR_ERICSSON"],
                        "threshold": 99
                    },
                    "2G CDR (%)": {
                        "columns": ["CDR_ERICSSON"],
                        "threshold": 1
                    },
                    "2G CBR (%)": {
                        "columns": ["CBR_ERICSSON"],
                        "threshold": 1
                    },
                    "2G Cell Availability Rate (%)": {
                        "columns": ["CELL_AVAILABILITY_RATE_ERICSSON"],
                        "threshold": 99
                    },
                    "2G TCH Availability Rate (%)": {
                        "columns": ["TCH_AVAILABILITY_RATE_ERICSSON"],
                        "threshold": None
                    },
                    "2G TCH Congestion Rate (%)": {
                        "columns": ["TCH_CONGESTION_RATE_ERICSSON"],
                        "threshold": None
                    },
                    "2G SDCCH Drop Rate (%)": {
                        "columns": ["SDCCH_DROP_RATE_ERICSSON"],
                        "threshold": None
                    },
                    "2G SDCCH Blocking Rate (%)": {
                        "columns": ["SDCCH_BLOCKING_RATE_ERICSSON"],
                        "threshold": None
                    },
                    "2G SDCCH Congestion Rate (%)": {
                        "columns": ["SDCCH_CONGESTION_RATE_ERICSSON"],
                        "threshold": None
                    },
                    "2G SDCCH Traffic (Erlang)": {
                        "columns": ["SDCCH_TRAFFIC_ERICSSON"],
                        "threshold": None
                    },
                    "2G Downtime Manual": {
                        "columns": ["DOWNTIME_MANUAL"],
                        "threshold": None
                    },
                    "2G Traffic Data (GB)": {
                        "columns": ["TRAFFIC_DATA_GB_ERICSSON"],
                        "threshold": None
                    },
                    "2G Traffic Voice": {
                        "columns": ["TRAFFIC_VOIX_ERICSSON"],
                        "threshold": None
                    },
                },

                # Add batches here when ready:
                # "zone_north": {"label": "North Zone", "cells": _ERICSSON_2G_ZONE_NORTH},
                "batches": {
                     "cluster_1": {
                        "label": "LAC TAC CHANGE",
                        "cells": _ERICSSON_2G_LAC_TAC_CLUSTER_1,
                    },
                     "cluster_2": {
                        "label": "ERICSSON 1000 Plus Cell Improvement ",
                        "cells": _ERICSSON_2G_10_MARS_1000Plus_Cell,
                    },
                },
            },

            # -----------------------------------------------------------------
            # Huawei 2G
            # -----------------------------------------------------------------
            "huawei": {
                "label"    : "Huawei",
                "sql_file" : "huawei_2g.sql",
                "date_col" : "h.date",
                "time_col" : "h.time",
                "cell_col" : "h.CELL_NAME",

                "kpi_groups": {
                    "CSSR (%)": {
                        "columns": ["CSSR_HUAWEI"],
                        "threshold": 99
                    },
                    "CDR (%)": {
                        "columns": ["CDR_HUAWEI"],
                        "threshold": 1
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
                    },
                },

                "batches": {
                    "cluster_1": {
                        "label": "110 Cell impovment 10 Mars",
                        "cells": _HUAWEI_2G_CLUSTER_1,
                    },
                    "cluster_2": {
                        "label": "160 cell action worst cell 10 mars",
                        "cells": _HUAWEI_2G_CLUSTER_2,
                    },
                     "cluster_3": {
                        "label": "29 CELL ABDEL_AZIZ",
                        "cells": _HUAWEI_2G_CELL_29_MARCH,
                    },
                },
            },
        },
    },

    # =========================================================================
    # 3G
    # =========================================================================
    "3g": {
        "label": "3G",
        "vendors": {

            # -----------------------------------------------------------------
            # Ericsson 3G
            # -----------------------------------------------------------------
            "ericsson": {
                "label"    : "Ericsson",
                "sql_file" : "ericsson_3g.sql",
                "date_col" : "DATE",
                "time_col" : "TIME",
                "cell_col" : "CELL_NAME",

                "kpi_groups": {
                    "3G CS CSSR (%)": {
                        "columns": ["CS_CSSR"],
                        "threshold": None
                    },
                    "3G CS Drop Rate (%)": {
                        "columns": ["CS_DROP"],
                        "threshold": None
                    },
                    "3G CS CBR (%)": {
                        "columns": ["CS_CBR"],
                        "threshold": None
                    },
                    "3G PS CSSR (%)": {
                        "columns": ["PS_CSSR"],
                        "threshold": None
                    },
                    "3G PS Drop Rate (%)": {
                        "columns": ["PS_DROP"],
                        "threshold": None
                    },
                    "3G DL Throughput (kbps)": {
                        "columns": ["DEBIT_DL"],
                        "threshold": None
                    },
                    "3G UL Throughput (kbps)": {
                        "columns": ["DEBIT_UL"],
                        "threshold": None
                    },
                    "3G UL Cell Throughput ARCEP (kbps)": {
                        "columns": ["DEBIT_UL_CELL_ARCEP"],
                        "threshold": None
                    },
                    "3G Cell Availability (%)": {
                        "columns": ["CELL_AVAILABILITY"],
                        "threshold": None
                    },
                    "3G RL Add Success Rate (%)": {
                        "columns": ["RL_ADD_SUCCESS_RATE"],
                        "threshold": None
                    },
                    "3G IRAT HO Success Rate (%)": {
                        "columns": ["IRAT_HO_SUCCESS_RATE"],
                        "threshold": None
                    },
                    "3G Traffic Voice": {
                        "columns": ["TRAFFIC_VOIX"],
                        "threshold": None
                    },
                    "3G Traffic Data (GB)": {
                        "columns": ["TRAFFIC_DATA_GB"],
                        "threshold": None
                    },
                },

                # Add batches here when ready:
                # "zone_north": {"label": "North Zone", "cells": _ERICSSON_3G_ZONE_NORTH},
                "batches": {
                    "lac_tac_change": {"label": "LAC TAC Change", "cells": _ERICSSON_3G_CLUSTER_1},
                },
            },
        },
    },

    # =========================================================================
    # 4G
    # =========================================================================
    "4g": {
        "label": "4G",
        "vendors": {

            # -----------------------------------------------------------------
            # Ericsson 4G
            # -----------------------------------------------------------------
            "ericsson": {
                "label"    : "Ericsson",
                "sql_file" : "ericsson_4g.sql",
                "date_col" : "DATE",
                "time_col" : "TIME",
                "cell_col" : "CELL_NAME",

                "kpi_groups": {
                    "4G PS CSSR (%)": {
                        "columns": ["PS_CSSR"],
                        "threshold": None
                    },
                    "4G ERAB Drop Rate (%)": {
                        "columns": ["ERAB_DROP"],
                        "threshold": None
                    },
                    "4G DL Cell Throughput (kbps)": {
                        "columns": ["DEBIT_DL"],
                        "threshold": None
                    },
                    "4G UL Cell Throughput (kbps)": {
                        "columns": ["DEBIT_UL"],
                        "threshold": None
                    },
                    "4G DL User Throughput (kbps)": {
                        "columns": ["DL_USER_THP"],
                        "threshold": None
                    },
                    "4G UL User Throughput (kbps)": {
                        "columns": ["UL_USER_THP"],
                        "threshold": None
                    },
                    "4G Intra HO Success Rate (%)": {
                        "columns": ["INTRA_HOSR"],
                        "threshold": None
                    },
                    "4G Inter HO Success Rate (%)": {
                        "columns": ["INTER_HOSR"],
                        "threshold": None
                    },
                    "4G PRB Utilization (%)": {
                        "columns": ["PRB_UTILIZATION"],
                        "threshold": None
                    },
                    "4G PRB Utilization DL New (%)": {
                        "columns": ["PRB_UTILIZATION_DL_NEW"],
                        "threshold": None
                    },
                    "4G Cell Availability with Manual (%)": {
                        "columns": ["CELL_AVAILABILITY_WITH_MANUAL"],
                        "threshold": None
                    },
                    "4G Cell Availability (%)": {
                        "columns": ["CELL_AVAILABILITY"],
                        "threshold": None
                    },
                    "4G CSFB Success Rate (%)": {
                        "columns": ["CSFB_SR"],
                        "threshold": None
                    },
                    "4G ERAB Failures (count)": {
                        "columns": ["LTE_ERAB_FAILURE"],
                        "threshold": None
                    },
                    "4G Active Users": {
                        "columns": ["active_user"],
                        "threshold": None
                    },
                    "4G Traffic Data (GB)": {
                        "columns": ["TRAFFIC_DATA_GB"],
                        "threshold": None
                    },
                },

                # Add batches here when ready:
                # "zone_north": {"label": "North Zone", "cells": _ERICSSON_4G_ZONE_NORTH},
                "batches": {
                    "lac_tac_change": {"label": "LAC TAC Change", "cells": _ERICSSON_4G_CLUSTER_1},
                },
            },
        },
    },
}
