# Backtesting specific configuration

# Normalize all prices based on relation between adj_close and close
NORMALIZE_PRICES = True

# Normalize volume based on relation between adj_close and close
NORMALIZE_VOLUME = False


# Initial portfolio capital
INITIAL_CAPITAL = 100000.00

# Number of decimals used for rounding prices
ROUND_DECIMALS = 2
ROUND_DECIMALS_BELOW_ONE = 3

# Position size needs to be on increments of ROUND_LOT_SIZE
ROUND_LOT_SIZE = 10

# If both COMMISSION_FIXED and COMMISSION_PCT are set, both will be charged on each trade
# Fixed commission charged on each trade
COMMISSION_FIXED = 0.0
# Percentage commission charged on each trade
COMMISSION_PCT = 0.0008 # IB fixed commission Australia
# Minimum commission to be charged
COMMISSION_MIN = 0.0


# Used by portfolio to calculate limit_prices and estimated cost for Orders
MAX_SLIPPAGE = 0.0005

# Max number of concurrent open long positions
MAX_LONG_POSITIONS = 5
MAX_SHORT_POSITIONS = 0
# POSITION_SIZE has no default value.
# It is either derived from 1/MAX_LONG_POSITIONS or set by strategy, and is
# represented as percentage of portfolio level equity

# Adjusts position if there isn't enough cash available
ADJUST_POSITION_DOWN = True

# Flags backtest results as dangerous when the fraction of returns are gained in a single trade
THRESHOLD_DANGEROUS_TRADE = 0.20

# IB specific parameters
EXCHANGE = 'ASX'
SEC_TYPE = 'STK'
CURRENCY = 'AUD'

# List of symbols

# For ASX symbols YAHOO_SYMBOL_APPENDIX must be '.AX'
ASX_20 = ['AMP','ANZ','BHP','BXB','CBA','CSL','IAG','MQG','NAB','ORG','QBE','RIO','SCG','SUN','TLS','WBC','WES','WFD','WOW','WPL']
ASX_50 = ['AGL','AIO','AMC','AMP','ANZ','APA','ASX','AZJ','BHP','BXB','CBA','CCL','CPU','CSL','CTX','CWN','DXS','GMG','GPT','IAG','IPL','JHX','LLC','MGR','MPL','MQG','NAB','NCM','ORG','ORI','OSH','QBE','RHC','RIO','S32','SCG','SEK','SGP','SHL','STO','SUN','SYD','TCL','TLS','VCX','WBC','WES','WFD','WOW','WPL']
ASX_100 = ['ABC','AGL','AIO','ALL','ALQ','AMC','AMP','ANN','ANZ','APA','AST','ASX','AWC','AZJ','BEN','BHP','BLD','BOQ','BSL','BXB','CAR','CBA','CCL','CGF','CIM','COH','CPU','CSL','CSR','CTX','CWN','DLX','DMP','DOW','DUE','DXS','FLT','FMG','FXJ','GMG','GNC','GPT','HGG','HSO','HVN','IAG','IFL','ILU','IOF','IPL','JBH','JHX','LLC','MFG','MGR','MPL','MQG','NAB','NCM','NVT','ORA','ORG','ORI','OSH','PPT','PRY','QAN','QBE','QUB','REA','REC','RHC','RIO','RMD','S32','SCG','SEK','SGH','SGM','SGP','SGR','SHL','SKI','SPO','STO','SUN','SYD','TAH','TCL','TLS','TPM','TTS','TWE','VCX','WBC','WES','WFD','WOR','WOW','WPL']
ASX_200 = ['AAC','AAD','ABC','ABP','AGL','AHG','AHY','AIO','ALL','ALQ','ALU','AMC','AMP','ANN','ANZ','AOG','APA','APN','ARB','ARI','ASB','AST','ASX','AWC','AWE','AZJ','BAP','BEN','BGA','BHP','BKL','BLD','BOQ','BPT','BRG','BRS','BSL','BTT','BWP','BXB','CAB','CAR','CBA','CCL','CCP','CDD','CGF','CHC','CIM','CMW','COH','CPU','CQR','CSL','CSR','CTD','CTX','CVO','CWN','DLS','DLX','DMP','DOW','DSH','DUE','DXS','EHE','EVN','FBU','FLT','FMG','FPH','FXJ','FXL','GEM','GMA','GMG','GNC','GOZ','GPT','GTY','GUD','GWA','GXL','HGG','HSO','HVN','IAG','IFL','IGO','ILU','IOF','IPL','IRE','IVC','JBH','JHC','JHX','KAR','LLC','LNG','MFG','MGR','MIN','MMS','MND','MPL','MQA','MQG','MSB','MTR','MTS','MTU','MYO','MYR','MYX','NAB','NCM','NEC','NSR','NST','NUF','NVT','NWS','OFX','ORA','ORG','ORI','OSH','OZL','PBG','PDN','PGH','PMV','PPT','PRY','PTM','QAN','QBE','QUB','REA','REC','REG','RFG','RHC','RIO','RMD','RRL','S32','SAI','SCG','SCP','SDF','SEK','SFR','SGH','SGM','SGP','SGR','SHL','SHV','SIP','SKC','SKI','SKT','SPK','SPO','SRX','STO','SUL','SUN','SVW','SWM','SXL','SYD','SYR','TAH','TCL','TEN','TGR','TLS','TME','TNE','TPI','TPM','TTS','TWE','VCX','VED','VOC','VRL','VRT','WBC','WES','WFD','WHC','WOR','WOW','WPL','WSA']
ASX_300 = ['AAC','AAD','ABC','ABP','ACR','ADH','AGI','AGL','AHG','AHY','AIA','AIO','AJA','ALL','ALQ','ALU','AMC','AMP','ANN','ANZ','AOG','APA','API','APN','APO','AQG','ARB','ARF','ARI','ASB','AST','ASX','AWC','AWE','AZJ','BAL','BAP','BBG','BDR','BEN','BGA','BHP','BKL','BKN','BKW','BLD','BNO','BOQ','BPT','BRG','BRS','BSL','BTT','BWP','BXB','CAB','CAJ','CAR','CBA','CCL','CCP','CCV','CDD','CGF','CHC','CIM','CLH','CMW','CNU','COH','CPU','CQR','CSL','CSR','CSV','CTD','CTX','CVO','CWN','CWP','DCG','DLS','DLX','DMP','DNA','DOW','DSH','DUE','DXS','ECX','EHE','ELD','EPW','EQTDA','EVN','EWC','FAR','FBU','FET','FLT','FMG','FPH','FSF','FXJ','FXL','GBT','GDI','GEM','GHC','GMA','GMF','GMG','GNC','GOR','GOZ','GPT','GTY','GUD','GWA','GXL','HFA','HFR','HGG','HIL','HPI','HSN','HSO','HVN','IAG','IDR','IFL','IFM','IFN','IGO','ILU','IMF','INA','IOF','IPD','IPH','IPL','IPP','IRE','ISD','ISU','IVC','JBH','JHC','JHX','KAR','KCN','KMD','LLC','LNG','LYC','MFG','MGC','MGR','MGX','MIN','MLD','MLX','MML','MMS','MND','MOC','MPL','MQA','MQG','MRM','MSB','MTR','MTS','MTU','MVF','MYO','MYR','MYX','NAB','NAN','NCM','NEC','NHF','NSR','NST','NUF','NVT','NWS','NXT','OFX','OGC','OML','ORA','ORE','ORG','ORI','OSH','OZL','PAC','PBG','PDN','PGH','PMV','PPT','PRG','PRT','PRU','PRY','PTM','QAN','QBE','QUB','RCG','RCR','REA','REC','REG','RFG','RHC','RIC','RIO','RKN','RMD','RRL','RSG','S32','SAI','SAR','SBM','SCG','SCP','SDF','SEA','SEH','SEK','SFR','SGF','SGH','SGM','SGN','SGP','SGR','SHJ','SHL','SHV','SIP','SKC','SKI','SKT','SMX','SPK','SPL','SPO','SRX','STO','SUL','SUN','SVW','SWM','SXL','SXY','SYD','SYR','TAH','TCL','TEN','TFC','TGA','TGR','TIX','TLS','TME','TNE','TOX','TPI','TPM','TRS','TTS','TWE','UGL','UXC','VCX','VED','VLW','VOC','VRL','VRT','WBA','WBC','WEB','WES','WFD','WHC','WOR','WOW','WPL','WSA']
ASX_ALL_ORDINARIES = ['3PL','AAC','AAD','AAI','ABA','ABC','ABP','ACO','ACR','ACX','ADH','ADJ','ADO','AFA','AGG','AGI','AGL','AGO','AHD','AHG','AHY','AHZ','AIA','AIO','AJA','AJD','AJL','AKP','ALK','ALL','ALQ','ALU','AMA','AMC','AMI','AMP','ANN','ANZ','AOG','APA','APE','API','APN','APO','APZ','AQG','AQZ','ARB','ARF','ARI','ASB','ASH','ASL','AST','ASX','ASZ','ATU','AUB','AVB','AVJ','AWC','AWE','AWN','AZJ','BAL','BAP','BBG','BCI','BDR','BEN','BFG','BGA','BGL','BHP','BKL','BKN','BKW','BLA','BLD','BLX','BLY','BNO','BOC','BOQ','BPA','BPT','BRG','BRS','BRU','BSE','BSL','BTT','BWP','BXB','CAB','CAJ','CAR','CBA','CCL','CCP','CCV','CDA','CDD','CDP','CDU','CGF','CGH','CHC','CII','CIM','CKF','CLH','CLX','CMA','CMW','CNU','COE','COH','CPU','CQR','CSL','CSR','CSV','CTD','CTX','CUP','CUV','CVC','CVN','CVO','CVW','CWN','CWP','DCG','DDR','DLS','DLX','DMP','DNA','DOW','DRM','DSH','DTL','DUE','DVN','DWS','DXS','ECX','EHE','EHL','ELD','EML','ENN','EPW','EPX','EQTDA','ERA','ESV','EVN','EWC','EZL','FAN','FAR','FBU','FET','FLK','FLN','FLT','FMG','FND','FNP','FPH','FRI','FSA','FSF','FXJ','FXL','GBT','GDI','GEG','GEM','GFY','GHC','GID','GJT','GMA','GMF','GMG','GNC','GNE','GNG','GOR','GOW','GOZ','GPT','GRR','GTY','GUD','GWA','GXL','GZL','HFA','HFR','HGG','HIL','HLO','HPI','HSN','HSO','HTA','HUO','HVN','HZN','IAG','ICQ','IDR','IFL','IFM','IFN','IGO','ILU','IMD','IMF','INA','IOF','IPD','IPH','IPL','IPP','IQE','IRD','IRE','IRI','ISD','ISU','IVC','IWG','JBH','JHC','JHX','KAM','KAR','KCN','KMD','KPL','KRM','KSC','LAU','LEP','LHC','LIC','LLC','LNG','LNR','LOV','LYC','MAH','MAQ','MCP','MCR','MDL','MFG','MGC','MGR','MGX','MIG','MIN','MLB','MLD','MLX','MML','MMS','MND','MNF','MNY','MOC','MPL','MQA','MQG','MRM','MSB','MTR','MTS','MTU','MVF','MXI','MYO','MYR','MYS','MYX','NAB','NAN','NCK','NCM','NEA','NEC','NEU','NHC','NHF','NSR','NST','NTU','NUF','NVT','NWF','NWH','NWS','NXT','OBJ','OCL','OEL','OFX','OGC','OMH','OML','ONT','ORA','ORE','ORG','ORI','ORL','OSH','OZL','PAC','PAN','PAY','PBD','PBG','PBT','PDN','PEA','PEN','PFL','PGH','PGR','PHI','PME','PMP','PMV','POS','PPC','PPG','PPT','PRG','PRT','PRU','PRY','PSQ','PSY','PTM','QAN','QBE','QUB','RCG','RCR','RCT','RDF','REA','REC','REG','REH','REX','RFF','RFG','RHC','RHL','RHP','RIC','RIO','RKN','RMD','RRL','RSG','RUL','RWH','S32','SAI','SAR','SBM','SCG','SCP','SDA','SDF','SDG','SDL','SDM','SEA','SEH','SEK','SFH','SFR','SFX','SGF','SGH','SGM','SGN','SGP','SGR','SHJ','SHL','SHV','SIO','SIP','SIQ','SIV','SKC','SKI','SKT','SLK','SLM','SLR','SLX','SMX','SOL','SOM','SPH','SPK','SPL','SPO','SRF','SRV','SRX','SST','STO','SUL','SUN','SVW','SWL','SWM','SXL','SXY','SYD','SYR','TAH','TAP','TBR','TCL','TEN','TFC','TGA','TGP','TGR','TGS','TIG','TIX','TLS','TME','TNE','TOE','TOF','TOX','TPI','TPM','TRS','TRY','TTS','TWE','TZN','UBN','UGL','UNS','UOS','URF','UXC','VAH','VCX','VED','VLW','VOC','VRL','VRT','VTG','WBA','WBC','WCB','WEB','WES','WFD','WHC','WLC','WLF','WLL','WOR','WOW','WPL','WSA','WTP','YAL','ZIM','ZNZ']
ASX_ETFS = ['ZOZI','QOZ','IOZ','ILC','ISO','MVW','MVS','STW','SFY','SSO','UBA','VAS','VLC','VSO','QFN','QRE','MVA','MVB','MVE','MVR','SLF','OZF','OZR','VAP','ZYUS','QUS','GGUS','NDQ','UMAX','IAA','IBK','ITW','IKO','IHK','ISG','IRU','IZZ','IJP','IEM','IOO','IHOO','IVV','IHVV','IJH','IJR','IVE','IEU','KII','MGE','MHG','CETF','MOAT','QUAL','QMIX','WEMG','WDIV','WXHG','WXOZ','SPY','UBW','UBE','UBJ','UBU','VEU','VGE','VGS','VGAD','VTS','IXI','IXJ','IXP','GDX','DJRE','ZYAU','AOD','HVST','BEAR','BBOZ','YMAX','GEAR','IHD','RARI','RDV','RVL','SYI','VHY','DIV','ETF','ZCNH','ZUSD','EEU','POU','USD','AAA','IAF','ILB','IGB','RGB','RSM','RCB','BOND','GOVT','VAF','VGB','ZGOL','QAG','QAU','QCB','OOO','GOLD',]

# For NZX symbols YAHOO_SYMBOL_APPENDIX must be '.NZ'
NZX_50 = ['AIA','AIR','ANZ','ARG','ATM','CEN','CNU','COA','DIL','DNZ','EBO','FBU','FPH','FRE','FSF','GMT','GNE','HNZ','IFT','KMD','KPG','MEL','MET','MFT','MPG','MRP','NPX','NZX','OHE','PCT','PEB','PFI','POT','RBD','RYM','SKC','SKL','SKT','SPK','STU','SUM','TME','TPW','TWR','VCT','VHP','WBC','WHS','XRO','ZEL']
NZX_ALL_SECURITIES = ['ABA','AFI','AIA','AIR','ALF','AMP','ANZ','AOR','AORWA','APA','APN','ARG','ARV','ASBPA','ASBPB','ASD','ASF','ASP','ASR','ATM','AUG','AWF','AWK','BGR','BIL','BILRA','BIT','BLT','BRM','BRMWC','CAV','CDI','CEN','CMO','CNU','COA','CVT','DGL','DIL','DIV','DNZ','DOW','EBO','EMF','ERD','EUF','EUT','EVO','FBU','FCT','FIN','FLI','FNZ','FPH','FRE','FSF','GMT','GNE','GTK','GXH','HBY','HFL','HLG','HNZ','IFT','IKE','IQE','JFJ','JMO','JMOOA','KFL','KFLWC','KMD','KPG','KRK','MAD','MCK','MCKPA','MDZ','MEL','MET','MFT','MGL','MHI','MLN','MLNWB','MMH','MOA','MPG','MRP','MVN','MVT','MZY','NPT','NPX','NTL','NTLOA','NWF','NZF','NZO','NZR','NZX','OGC','OHE','OIC','OZY','PAY','PBG','PCT','PEB','PFI','PFIRG','PGC','PGW','PIL','POT','PPL','PPP','RAK','RBC','RBD','RYM','SAN','SCL','SCT','SCY','SEA','SEARA','SEK','SKC','SKL','SKO','SKT','SLG','SLI','SML','SPK','SPN','SPY','STU','SUM','TCL','TEM','TEN','TGG','THL','TIL','TLS','TME','TNR','TNZ','TPI','TPW','TRS','TTK','TWF','TWR','USF','USG','USM','USS','USV','VCT','VGL','VHP','VIL','WBC','WDT','WDTPA','WHS','WYN','XRO','ZEL']

# For BMFBovespa YAHOO_SYMBOL_APPENDIX must be '.SA'
IBOVESPA = ['ABEV3','BBAS3','BBDC3','BBDC4','BBSE3','BRAP4','BRFS3','BRKM5','BRML3','BRPR3','BVMF3','CCRO3','CESP6','CIEL3','CMIG4','CPFE3','CPLE6','CRUZ3','CSAN3','CSNA3','CTIP3','CYRE3','DTEX3','ECOR3','ELET3','ELET6','EMBR3','ENBR3','ESTC3','FIBR3','GFSA3','GGBR4','GOAU4','GOLL4','HGTX3','HYPE3','ITSA4','ITUB4','JBSS3','KLBN11','KROT3','LAME4','LREN3','MRFG3','MRVE3','MULT3','NATU3','OIBR4','PCAR4','PETR3','PETR4','POMO4','QUAL3','RENT3','RUMO3','SANB11','SBSP3','SMLE3','SUZB5','TBLE3','TIMP3','UGPA3','USIM5','VALE3','VALE5','VIVT4']
