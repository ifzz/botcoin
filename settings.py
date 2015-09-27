from datetime import timedelta, datetime
import logging
import os
import pandas as pd

# Pandas config
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 1000) 


# Logging config
VERBOSITY = 20
LOG_FORMAT = '# %(levelname)s:%(module)s - %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=VERBOSITY)


# Directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
SRC_DIR = os.path.join(BASE_DIR, 'src/')


# Data APIs
YAHOO_CHART_API = 'http://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range={}/csv'
YAHOO_API = 'http://ichart.finance.yahoo.com/table.csv?s={}&c={}&g={}'


# Backtesting specific configuration

# Normalize all prices based on relation between adj_close and close
NORMALIZE_PRICES = True

# Normalize volume based on relation between adj_close and close
NORMALIZE_VOLUME = False

# Dates to start and finish backtest
DATE_TO = datetime.now()
DATE_FROM = DATE_TO - timedelta(weeks=52)

# Initial portfolio capital
INITIAL_CAPITAL = 100000.00

# Number of decimals used for rounding prices 
ROUND_DECIMALS = 2

# If both COMMISSION_FIXED and COMMISSION_PCT are set, both will be charged on each trade
# Fixed commission charged on each trade
COMMISSION_FIXED = 0.0
# Percentage commission charged on each trade
COMMISSION_PCT = 0.0008 # IB fixed commission Australia

# Used by portfolio to calculate limit_prices and estimated cost for Orders
MAX_SLIPPAGE = 0.0005

# Max number of concurrent open long positions
MAX_LONG_POSITIONS = 5
MAX_SHORT_POSITIONS = 0
# Represented as percentage of portfolio level equity
POSITION_SIZE = 1.0/MAX_LONG_POSITIONS

# Adjusts position if there isn't enough cash available
ADJUST_POSITION_DOWN = True

# Flags backtest results as dangerous when the fraction of returns are gained in a single trade
THRESHOLD_DANGEROUS_TRADE = 0.20

# List of symbols
SP_500 = ['ABT','ABBV','ACN','ACE','ADBE','ADT','AAP','AES','AET','AFL','AMG','A','GAS','APD','ARG','AKAM','AA','AGN','ALXN','ALLE','ADS','ALL','ALTR','MO','AMZN','AEE','AAL','AEP','AXP','AIG','AMT','AMP','ABC','AME','AMGN','APH','APC','ADI','AON','APA','AIV','AAPL','AMAT','ADM','AIZ','T','ADSK','ADP','AN','AZO','AVGO','AVB','AVY','BHI','BLL','BAC','BK','BCR','BXLT','BAX','BBT','BDX','BBBY','BRK-B','BBY','BIIB','BLK','HRB','BA','BWA','BXP','BSX','BMY','BRCM','BF-B','CHRW','CA','CVC','COG','CAM','CPB','COF','CAH','HSIC','KMX','CCL','CAT','CBG','CBS','CELG','CNP','CTL','CERN','CF','SCHW','CHK','CVX','CMG','CB','CI','XEC','CINF','CTAS','CSCO','C','CTXS','CLX','CME','CMS','COH','KO','CCE','CTSH','CL','CPGX','CMCSA','CMA','CSC','CAG','COP','CNX','ED','STZ','GLW','COST','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DLPH','DAL','XRAY','DVN','DO','DFS','DISCA','DISCK','DG','DLTR','D','DOV','DOW','DPS','DTE','DD','DUK','DNB','ETFC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMC','EMR','ENDP','ESV','ETR','EOG','EQT','EFX','EQIX','EQR','ESS','EL','ES','EXC','EXPE','EXPD','ESRX','XOM','FFIV','FB','FAST','FDX','FIS','FITB','FSLR','FE','FISV','FLIR','FLS','FLR','FMC','FTI','F','FOSL','BEN','FCX','FTR','GME','GPS','GRMN','GD','GE','GGP','GIS','GM','GPC','GNW','GILD','GS','GT','GOOGL','GOOG','GWW','HAL','HBI','HOG','HAR','HRS','HIG','HAS','HCA','HCP','HCN','HP','HES','HPQ','HD','HON','HRL','HSP','HST','HCBK','HUM','HBAN','ITW','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IRM','JEC','JBHT','JNJ','JCI','JOY','JPM','JNPR','KSU','K','KEY','GMCR','KMB','KIM','KMI','KLAC','KSS','KHC','KR','LB','LLL','LH','LRCX','LM','LEG','LEN','LVLT','LUK','LLY','LNC','LLTC','LMT','L','LOW','LYB','MTB','MAC','M','MNK','MRO','MPC','MAR','MMC','MLM','MAS','MA','MAT','MKC','MCD','MHFI','MCK','MJN','WRK','MDT','MRK','MET','KORS','MCHP','MU','MSFT','MHK','TAP','MDLZ','MON','MNST','MCO','MS','MOS','MSI','MUR','MYL','NDAQ','NOV','NAVI','NTAP','NFLX','NWL','NFX','NEM','NWSA','NEE','NLSN','NKE','NI','NBL','JWN','NSC','NTRS','NOC','NRG','NUE','NVDA','ORLY','OXY','OMC','OKE','ORCL','OI','PCAR','PLL','PH','PDCO','PAYX','PYPL','PNR','PBCT','POM','PEP','PKI','PRGO','PFE','PCG','PM','PSX','PNW','PXD','PBI','PCL','PNC','RL','PPG','PPL','PX','PCP','PCLN','PFG','PG','PGR','PLD','PRU','PEG','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RRC','RTN','O','RHT','REGN','RF','RSG','RAI','RHI','ROK','COL','ROP','ROST','RCL','R','CRM','SNDK','SCG','SLB','SNI','STX','SEE','SRE','SHW','SIAL','SIG','SPG','SWKS','SLG','SJM','SNA','SO','LUV','SWN','SE','STJ','SWK','SPLS','SBUX','HOT','STT','SRCL','SYK','STI','SYMC','SYY','TROW','TGT','TEL','TE','TGNA','THC','TDC','TSO','TXN','TXT','HSY','TRV','TMO','TIF','TWX','TWC','TJX','TMK','TSS','TSCO','RIG','TRIP','FOXA','TSN','TYC','USB','UA','UNP','UNH','UPS','URI','UTX','UHS','UNM','URBN','VFC','VLO','VAR','VTR','VRSN','VZ','VRTX','VIAB','V','VNO','VMC','WMT','WBA','DIS','WM','WAT','ANTM','WFC','WDC','WU','WY','WHR','WFM','WMB','WEC','WYN','WYNN','XEL','XRX','XLNX','XL','XYL','YHOO','YUM','ZBH','ZION','ZTS']

ASX_20 = ['AMP.AX','ANZ.AX','BHP.AX','BXB.AX','CSL.AX','CBA.AX','IAG.AX','MQG.AX','NAB.AX','ORG.AX','QBE.AX','RIO.AX','SCG.AX','SUN.AX','TLS.AX','WES.AX','WFD.AX','WBC.AX','WPL.AX','WOW.AX']
ASX_50 = ['AGL.AX','AIO.AX','AMC.AX','AMP.AX','ANZ.AX','APA.AX','ASX.AX','AZJ.AX','BHP.AX','BXB.AX','CBA.AX','CCL.AX','CPU.AX','CSL.AX','CTX.AX','CWN.AX','DXS.AX','FDC.AX','GMG.AX','GPT.AX','IAG.AX','IPL.AX','JHX.AX','LLC.AX','MGR.AX','MPL.AX','MQG.AX','NAB.AX','NCM.AX','ORG.AX','ORI.AX','OSH.AX','QBE.AX','RHC.AX','RIO.AX','S32.AX','SCG.AX','SEK.AX','SGP.AX','SHL.AX','STO.AX','SUN.AX','SYD.AX','TCL.AX','TLS.AX','WBC.AX','WES.AX','WFD.AX','WOW.AX','WPL.AX',]   
ASX_100 = ['ABC.AX','AGL.AX','AIO.AX','ALL.AX','ALQ.AX','AMC.AX','AMP.AX','ANN.AX','ANZ.AX','APA.AX','AST.AX','ASX.AX','AWC.AX','AZJ.AX','BEN.AX','BHP.AX','BLD.AX','BOQ.AX','BSL.AX','BXB.AX','CAR.AX','CBA.AX','CCL.AX','CGF.AX','CIM.AX','COH.AX','CPU.AX','CSL.AX','CSR.AX','CTX.AX','CWN.AX','DLX.AX','DMP.AX','DOW.AX','DUE.AX','DXS.AX','EGP.AX','FDC.AX','FLT.AX','FMG.AX','FXJ.AX','GMG.AX','GNC.AX','GPT.AX','HGG.AX','HSO.AX','HVN.AX','IAG.AX','IFL.AX','ILU.AX','IOF.AX','IPL.AX','JBH.AX','JHX.AX','LLC.AX','MFG.AX','MGR.AX','MPL.AX','MQG.AX','MTS.AX','NAB.AX','NCM.AX','NVT.AX','ORA.AX','ORG.AX','ORI.AX','OSH.AX','PPT.AX','PRY.AX','QAN.AX','QBE.AX','REA.AX','REC.AX','RHC.AX','RIO.AX','RMD.AX','S32.AX','SCG.AX','SEK.AX','SGH.AX','SGM.AX','SGP.AX','SHL.AX','SKI.AX','STO.AX','SUN.AX','SYD.AX','TAH.AX','TCL.AX','TLS.AX','TPI.AX','TPM.AX','TTS.AX','TWE.AX','WBC.AX','WES.AX','WFD.AX','WOR.AX','WOW.AX','WPL.AX']
ASX_200 = ['AAC.AX','AAD.AX','ABC.AX','ABP.AX','AGI.AX','AGL.AX','AHG.AX','AHY.AX','AIO.AX','ALL.AX','ALQ.AX','AMC.AX','AMP.AX','ANN.AX','ANZ.AX','AOG.AX','APA.AX','APN.AX','ARB.AX','ARI.AX','AST.AX','ASX.AX','AWC.AX','AWE.AX','AZJ.AX','BEN.AX','BGA.AX','BHP.AX','BKN.AX','BLD.AX','BOQ.AX','BPT.AX','BRG.AX','BSL.AX','BTT.AX','BWP.AX','BXB.AX','CAB.AX','CAR.AX','CBA.AX','CCL.AX','CCP.AX','CDD.AX','CGF.AX','CHC.AX','CIM.AX','CMW.AX','COH.AX','CPU.AX','CQR.AX','CSL.AX','CSR.AX','CTD.AX','CTX.AX','CVO.AX','CWN.AX','DLS.AX','DLX.AX','DMP.AX','DOW.AX','DSH.AX','DUE.AX','DXS.AX','EGP.AX','EHE.AX','EVN.AX','FBU.AX','FDC.AX','FLT.AX','FMG.AX','FPH.AX','FXJ.AX','FXL.AX','GEM.AX','GMA.AX','GMG.AX','GNC.AX','GOZ.AX','GPT.AX','GUD.AX','GWA.AX','GXL.AX','HGG.AX','HSO.AX','HVN.AX','IAG.AX','IFL.AX','IGO.AX','ILU.AX','IOF.AX','IPL.AX','IRE.AX','IVC.AX','JBH.AX','JHC.AX','JHX.AX','KAR.AX','KMD.AX','LLC.AX','LNG.AX','MFG.AX','MGR.AX','MIN.AX','MMS.AX','MND.AX','MPL.AX','MQA.AX','MQG.AX','MRM.AX','MSB.AX','MTS.AX','MTU.AX','MYR.AX','MYX.AX','NAB.AX','NCM.AX','NEC.AX','NSR.AX','NST.AX','NUF.AX','NVT.AX','NWS.AX','OFX.AX','ORA.AX','ORG.AX','ORI.AX','OSH.AX','OZL.AX','PBG.AX','PDN.AX','PGH.AX','PMV.AX','PPT.AX','PRY.AX','PTM.AX','QAN.AX','QBE.AX','QUB.AX','REA.AX','REC.AX','REG.AX','RFG.AX','RHC.AX','RIO.AX','RMD.AX','RRL.AX','S32.AX','SAI.AX','SCG.AX','SCP.AX','SDF.AX','SEK.AX','SFR.AX','SGH.AX','SGM.AX','SGP.AX','SHL.AX','SHV.AX','SIP.AX','SIR.AX','SKC.AX','SKI.AX','SKT.AX','SPK.AX','SPO.AX','SRX.AX','STO.AX','SUL.AX','SUN.AX','SVW.AX','SWM.AX','SXL.AX','SXY.AX','SYD.AX','SYR.AX','TAH.AX','TCL.AX','TEN.AX','TGR.AX','TLS.AX','TME.AX','TNE.AX','TPI.AX','TPM.AX','TSE.AX','TTS.AX','TWE.AX','UGL.AX','VED.AX','VOC.AX','VRL.AX','VRT.AX','WBC.AX','WES.AX','WFD.AX','WHC.AX','WOR.AX','WOW.AX','WPL.AX','WSA.AX']
ASX_300 = ['AAC.AX','AAD.AX','ABC.AX','ABP.AX','ACR.AX','AFJ.AX','AGI.AX','AGL.AX','AGO.AX','AHG.AX','AHY.AX','AIA.AX','AIO.AX','AJA.AX','ALL.AX','ALQ.AX','ALU.AX','AMC.AX','AMP.AX','ANI.AX','ANN.AX','ANZ.AX','AOG.AX','APA.AX','API.AX','APN.AX','APO.AX','AQG.AX','ARB.AX','ARF.AX','ARI.AX','ASB.AX','ASL.AX','AST.AX','ASX.AX','AWC.AX','AWE.AX','AZJ.AX','BAP.AX','BBG.AX','BCI.AX','BDR.AX','BEN.AX','BGA.AX','BHP.AX','BKN.AX','BLD.AX','BNO.AX','BOQ.AX','BPT.AX','BRG.AX','BRU.AX','BSL.AX','BTT.AX','BWP.AX','BXB.AX','CAB.AX','CAJ.AX','CAR.AX','CBA.AX','CCL.AX','CCP.AX','CCV.AX','CDD.AX','CDU.AX','CGF.AX','CHC.AX','CIM.AX','CLH.AX','CMW.AX','CNU.AX','COH.AX','CPU.AX','CQR.AX','CSL.AX','CSR.AX','CSV.AX','CTD.AX','CTX.AX','CVO.AX','CWN.AX','CWP.AX','DCG.AX','DLS.AX','DLX.AX','DMP.AX','DNA.AX','DOW.AX','DSH.AX','DUE.AX','DXS.AX','EGP.AX','EHE.AX','EPW.AX','EQT.AX','ERA.AX','EVN.AX','EWC.AX','FAR.AX','FBU.AX','FDC.AX','FET.AX','FLT.AX','FMG.AX','FPH.AX','FSF.AX','FXJ.AX','FXL.AX','GBT.AX','GDI.AX','GEM.AX','GMA.AX','GMF.AX','GMG.AX','GNC.AX','GOZ.AX','GPT.AX','GUD.AX','GWA.AX','GXL.AX','HGG.AX','HIL.AX','HPI.AX','HSN.AX','HSO.AX','HVN.AX','HZN.AX','IAG.AX','IDR.AX','IFL.AX','IFM.AX','IFN.AX','IGO.AX','ILU.AX','IMF.AX','INA.AX','IOF.AX','IPD.AX','IPH.AX','IPL.AX','IPP.AX','IRE.AX','ISD.AX','ISU.AX','IVC.AX','JBH.AX','JHC.AX','JHX.AX','KAR.AX','KCN.AX','KMD.AX','LLC.AX','LNG.AX','LYC.AX','MFG.AX','MGR.AX','MGX.AX','MIN.AX','MLD.AX','MLX.AX','MML.AX','MMS.AX','MND.AX','MOC.AX','MPL.AX','MQA.AX','MQG.AX','MRM.AX','MSB.AX','MTR.AX','MTS.AX','MTU.AX','MVF.AX','MYR.AX','MYX.AX','NAB.AX','NAN.AX','NCM.AX','NEC.AX','NHF.AX','NSR.AX','NST.AX','NUF.AX','NVT.AX','NWH.AX','NWS.AX','NXT.AX','OFX.AX','OGC.AX','OML.AX','ORA.AX','ORE.AX','ORG.AX','ORI.AX','OSH.AX','OZL.AX','PBG.AX','PDN.AX','PGH.AX','PMV.AX','PPT.AX','PRG.AX','PRT.AX','PRU.AX','PRY.AX','PTM.AX','QAN.AX','QBE.AX','QUB.AX','RCG.AX','RCR.AX','REA.AX','REC.AX','REG.AX','RFG.AX','RHC.AX','RIC.AX','RIO.AX','RKN.AX','RMD.AX','RRL.AX','RSG.AX','S32.AX','SAI.AX','SAR.AX','SCG.AX','SCP.AX','SDF.AX','SEA.AX','SEH.AX','SEK.AX','SFR.AX','SGF.AX','SGH.AX','SGM.AX','SGN.AX','SGP.AX','SHJ.AX','SHL.AX','SHV.AX','SIP.AX','SIR.AX','SKC.AX','SKE.AX','SKI.AX','SKT.AX','SLR.AX','SMX.AX','SPK.AX','SPL.AX','SPO.AX','SRX.AX','STO.AX','SUL.AX','SUN.AX','SVW.AX','SWM.AX','SXL.AX','SXY.AX','SYD.AX','SYR.AX','TAH.AX','TCL.AX','TEN.AX','TFC.AX','TGA.AX','TGR.AX','TGS.AX','TIX.AX','TLS.AX','TME.AX','TNE.AX','TOX.AX','TPI.AX','TPM.AX','TRG.AX','TRS.AX','TSE.AX','TTS.AX','TWE.AX','UGL.AX','UXC.AX','VED.AX','VLW.AX','VOC.AX','VRL.AX','VRT.AX','WBC.AX','WEB.AX','WES.AX','WFD.AX','WHC.AX','WOR.AX','WOW.AX','WPL.AX','WSA.AX']
ASX_ALL_ORDINARIES = ['3PL.AX','AAC.AX','AAD.AX','AAI.AX','ABA.AX','ABC.AX','ABP.AX','ACO.AX','ACR.AX','ACX.AX','ADJ.AX','ADO.AX','AFA.AX','AFJ.AX','AGG.AX','AGI.AX','AGL.AX','AGO.AX','AHD.AX','AHG.AX','AHY.AX','AHZ.AX','AIA.AX','AIO.AX','AJA.AX','AJD.AX','AJL.AX','AKP.AX','ALK.AX','ALL.AX','ALQ.AX','ALU.AX','AMA.AX','AMC.AX','AMI.AX','AMP.AX','ANI.AX','ANN.AX','ANZ.AX','AOG.AX','APA.AX','APE.AX','API.AX','APN.AX','APO.AX','APZ.AX','AQG.AX','AQZ.AX','ARB.AX','ARF.AX','ARI.AX','ASB.AX','ASH.AX','ASL.AX','AST.AX','ASX.AX','ASZ.AX','ATU.AX','AUB.AX','AVB.AX','AVJ.AX','AWC.AX','AWE.AX','AWN.AX','AZJ.AX','BAL.AX','BAP.AX','BBG.AX','BCI.AX','BDR.AX','BEN.AX','BFG.AX','BGA.AX','BGL.AX','BHP.AX','BKL.AX','BKN.AX','BKW.AX','BLA.AX','BLD.AX','BLX.AX','BLY.AX','BNO.AX','BOC.AX','BOQ.AX','BPA.AX','BPT.AX','BRG.AX','BRU.AX','BSE.AX','BSL.AX','BTT.AX','BWP.AX','BXB.AX','CAB.AX','CAJ.AX','CAR.AX','CBA.AX','CCL.AX','CCP.AX','CCV.AX','CDA.AX','CDD.AX','CDP.AX','CDU.AX','CGF.AX','CGH.AX','CHC.AX','CII.AX','CIM.AX','CKF.AX','CLH.AX','CLX.AX','CMA.AX','CMW.AX','CNU.AX','COE.AX','COH.AX','COK.AX','CPU.AX','CQR.AX','CSL.AX','CSR.AX','CSV.AX','CTD.AX','CTX.AX','CUP.AX','CUV.AX','CVC.AX','CVN.AX','CVO.AX','CVW.AX','CWN.AX','CWP.AX','DCG.AX','DDR.AX','DLS.AX','DLX.AX','DMP.AX','DNA.AX','DOW.AX','DRM.AX','DSH.AX','DTL.AX','DUE.AX','DVN.AX','DWS.AX','DXS.AX','EGP.AX','EHE.AX','EHL.AX','ELD.AX','EML.AX','ENE.AX','ENN.AX','EPW.AX','EPX.AX','EQT.AX','ERA.AX','ESV.AX','EVN.AX','EWC.AX','EZL.AX','FAN.AX','FAR.AX','FBU.AX','FDC.AX','FET.AX','FLK.AX','FLN.AX','FLT.AX','FMG.AX','FND.AX','FNP.AX','FPH.AX','FRI.AX','FSA.AX','FSF.AX','FXJ.AX','FXL.AX','GBT.AX','GDI.AX','GEG.AX','GEM.AX','GFY.AX','GHC.AX','GID.AX','GJT.AX','GMA.AX','GMF.AX','GMG.AX','GNC.AX','GNE.AX','GNG.AX','GOR.AX','GOW.AX','GOZ.AX','GPT.AX','GRR.AX','GUD.AX','GWA.AX','GXL.AX','GZL.AX','HFA.AX','HFR.AX','HGG.AX','HIL.AX','HLO.AX','HPI.AX','HSN.AX','HSO.AX','HTA.AX','HUO.AX','HVN.AX','HZN.AX','IAG.AX','ICQ.AX','IDR.AX','IFL.AX','IFM.AX','IFN.AX','IGO.AX','ILU.AX','IMD.AX','IMF.AX','INA.AX','IOF.AX','IPD.AX','IPH.AX','IPL.AX','IPP.AX','IQE.AX','IRD.AX','IRE.AX','IRI.AX','ISD.AX','ISU.AX','IVC.AX','IWG.AX','JBH.AX','JHC.AX','JHX.AX','KAM.AX','KAR.AX','KCN.AX','KMD.AX','KPL.AX','KRM.AX','KSC.AX','LAU.AX','LEP.AX','LHC.AX','LIC.AX','LLC.AX','LNG.AX','LNR.AX','LOV.AX','LYC.AX','MAH.AX','MAQ.AX','MCP.AX','MCR.AX','MDL.AX','MFG.AX','MGR.AX','MGX.AX','MIG.AX','MIN.AX','MLB.AX','MLD.AX','MLX.AX','MML.AX','MMS.AX','MND.AX','MNF.AX','MNY.AX','MOC.AX','MPL.AX','MQA.AX','MQG.AX','MRM.AX','MSB.AX','MTR.AX','MTS.AX','MTU.AX','MVF.AX','MXI.AX','MYR.AX','MYS.AX','MYX.AX','NAB.AX','NAN.AX','NCK.AX','NCM.AX','NEA.AX','NEC.AX','NEU.AX','NHC.AX','NHF.AX','NSR.AX','NST.AX','NTU.AX','NUF.AX','NVT.AX','NWF.AX','NWH.AX','NWS.AX','NXT.AX','OBJ.AX','OCL.AX','OEL.AX','OFX.AX','OGC.AX','OMH.AX','OML.AX','ONT.AX','ORA.AX','ORE.AX','ORG.AX','ORI.AX','ORL.AX','OSH.AX','OZL.AX','PAN.AX','PAY.AX','PBD.AX','PBG.AX','PBT.AX','PDN.AX','PEA.AX','PEN.AX','PFL.AX','PGH.AX','PGR.AX','PHI.AX','PME.AX','PMP.AX','PMV.AX','POS.AX','PPC.AX','PPG.AX','PPT.AX','PRG.AX','PRT.AX','PRU.AX','PRY.AX','PSQ.AX','PSY.AX','PTM.AX','QAN.AX','QBE.AX','QUB.AX','RCG.AX','RCR.AX','RCT.AX','RDF.AX','REA.AX','REC.AX','REG.AX','REH.AX','REX.AX','RFF.AX','RFG.AX','RHC.AX','RHL.AX','RHP.AX','RIC.AX','RIO.AX','RKN.AX','RMD.AX','RRL.AX','RSG.AX','RUL.AX','RWH.AX','S32.AX','SAI.AX','SAR.AX','SCG.AX','SCP.AX','SDA.AX','SDF.AX','SDG.AX','SDL.AX','SDM.AX','SEA.AX','SEH.AX','SEK.AX','SFH.AX','SFR.AX','SFX.AX','SGF.AX','SGH.AX','SGM.AX','SGN.AX','SGP.AX','SHJ.AX','SHL.AX','SHV.AX','SIO.AX','SIP.AX','SIQ.AX','SIR.AX','SIV.AX','SKC.AX','SKE.AX','SKI.AX','SKT.AX','SLK.AX','SLM.AX','SLR.AX','SLX.AX','SMX.AX','SOL.AX','SOM.AX','SPH.AX','SPK.AX','SPL.AX','SPO.AX','SRF.AX','SRV.AX','SRX.AX','SST.AX','STO.AX','SUL.AX','SUN.AX','SVW.AX','SWL.AX','SWM.AX','SXL.AX','SXY.AX','SYD.AX','SYR.AX','TAH.AX','TAP.AX','TBR.AX','TCL.AX','TEN.AX','TFC.AX','TGA.AX','TGP.AX','TGR.AX','TGS.AX','TIG.AX','TIX.AX','TLS.AX','TME.AX','TNE.AX','TOE.AX','TOF.AX','TOX.AX','TPI.AX','TPM.AX','TRG.AX','TRS.AX','TRY.AX','TSE.AX','TTS.AX','TWE.AX','TZN.AX','UBN.AX','UGL.AX','UNS.AX','UOS.AX','URF.AX','UXC.AX','VAH.AX','VED.AX','VEI.AX','VLW.AX','VOC.AX','VRL.AX','VRT.AX','VTG.AX','WBA.AX','WBC.AX','WCB.AX','WEB.AX','WES.AX','WFD.AX','WHC.AX','WLC.AX','WLF.AX','WLL.AX','WOR.AX','WOW.AX','WPL.AX','WSA.AX','WTP.AX','YAL.AX','ZIM.AX','ZNZ.AX']

NZX_50 = ['AIA.NZ','AIR.NZ','ANZ.NZ','ARG.NZ','ATM.NZ','CEN.NZ','CNU.NZ','COA.NZ','DIL.NZ','DNZ.NZ','EBO.NZ','FBU.NZ','FPH.NZ','FRE.NZ','FSF.NZ','GMT.NZ','GNE.NZ','HNZ.NZ','IFT.NZ','KMD.NZ','KPG.NZ','MEL.NZ','MET.NZ','MFT.NZ','MPG.NZ','MRP.NZ','NPX.NZ','NZX.NZ','OHE.NZ','PCT.NZ','PEB.NZ','PFI.NZ','POT.NZ','RBD.NZ','RYM.NZ','SKC.NZ','SKL.NZ','SKT.NZ','SPK.NZ','STU.NZ','SUM.NZ','TME.NZ','TPW.NZ','TWR.NZ','VCT.NZ','VHP.NZ','WBC.NZ','WHS.NZ','XRO.NZ','ZEL.NZ']
NZX_ALL_SECURITIES = ['ABA.NZ','AFI.NZ','AIA.NZ','AIR.NZ','ALF.NZ','AMP.NZ','ANZ.NZ','AOR.NZ','AORWA.NZ','APA.NZ','APN.NZ','ARG.NZ','ARV.NZ','ASBPA.NZ','ASBPB.NZ','ASD.NZ','ASF.NZ','ASP.NZ','ASR.NZ','ATM.NZ','AUG.NZ','AWF.NZ','AWK.NZ','BGR.NZ','BIL.NZ','BILRA.NZ','BIT.NZ','BLT.NZ','BRM.NZ','BRMWC.NZ','CAV.NZ','CDI.NZ','CEN.NZ','CMO.NZ','CNU.NZ','COA.NZ','CVT.NZ','DGL.NZ','DIL.NZ','DIV.NZ','DNZ.NZ','DOW.NZ','EBO.NZ','EMF.NZ','ERD.NZ','EUF.NZ','EUT.NZ','EVO.NZ','FBU.NZ','FCT.NZ','FIN.NZ','FLI.NZ','FNZ.NZ','FPH.NZ','FRE.NZ','FSF.NZ','GMT.NZ','GNE.NZ','GTK.NZ','GXH.NZ','HBY.NZ','HFL.NZ','HLG.NZ','HNZ.NZ','IFT.NZ','IKE.NZ','IQE.NZ','JFJ.NZ','JMO.NZ','JMOOA.NZ','KFL.NZ','KFLWC.NZ','KMD.NZ','KPG.NZ','KRK.NZ','MAD.NZ','MCK.NZ','MCKPA.NZ','MDZ.NZ','MEL.NZ','MET.NZ','MFT.NZ','MGL.NZ','MHI.NZ','MLN.NZ','MLNWB.NZ','MMH.NZ','MOA.NZ','MPG.NZ','MRP.NZ','MVN.NZ','MVT.NZ','MZY.NZ','NPT.NZ','NPX.NZ','NTL.NZ','NTLOA.NZ','NWF.NZ','NZF.NZ','NZO.NZ','NZR.NZ','NZX.NZ','OGC.NZ','OHE.NZ','OIC.NZ','OZY.NZ','PAY.NZ','PBG.NZ','PCT.NZ','PEB.NZ','PFI.NZ','PFIRG.NZ','PGC.NZ','PGW.NZ','PIL.NZ','POT.NZ','PPL.NZ','PPP.NZ','RAK.NZ','RBC.NZ','RBD.NZ','RYM.NZ','SAN.NZ','SCL.NZ','SCT.NZ','SCY.NZ','SEA.NZ','SEARA.NZ','SEK.NZ','SKC.NZ','SKL.NZ','SKO.NZ','SKT.NZ','SLG.NZ','SLI.NZ','SML.NZ','SPK.NZ','SPN.NZ','SPY.NZ','STU.NZ','SUM.NZ','TCL.NZ','TEM.NZ','TEN.NZ','TGG.NZ','THL.NZ','TIL.NZ','TLS.NZ','TME.NZ','TNR.NZ','TNZ.NZ','TPI.NZ','TPW.NZ','TRS.NZ','TTK.NZ','TWF.NZ','TWR.NZ','USF.NZ','USG.NZ','USM.NZ','USS.NZ','USV.NZ','VCT.NZ','VGL.NZ','VHP.NZ','VIL.NZ','WBC.NZ','WDT.NZ','WDTPA.NZ','WHS.NZ','WYN.NZ','XRO.NZ','ZEL.NZ']

IBOVESPA = ['ABEV3.SA','BBAS3.SA','BBDC3.SA','BBDC4.SA','BBSE3.SA','BRAP4.SA','BRFS3.SA','BRKM5.SA','BRML3.SA','BRPR3.SA','BVMF3.SA','CCRO3.SA','CESP6.SA','CIEL3.SA','CMIG4.SA','CPFE3.SA','CPLE6.SA','CRUZ3.SA','CSAN3.SA','CSNA3.SA','CTIP3.SA','CYRE3.SA','DTEX3.SA','ECOR3.SA','ELET3.SA','ELET6.SA','EMBR3.SA','ENBR3.SA','ESTC3.SA','FIBR3.SA','GFSA3.SA','GGBR4.SA','GOAU4.SA','GOLL4.SA','HGTX3.SA','HYPE3.SA','ITSA4.SA','ITUB4.SA','JBSS3.SA','KLBN11.SA','KROT3.SA','LAME4.SA','LREN3.SA','MRFG3.SA','MRVE3.SA','MULT3.SA','NATU3.SA','OIBR4.SA','PCAR4.SA','PETR3.SA','PETR4.SA','POMO4.SA','QUAL3.SA','RENT3.SA','RUMO3.SA','SANB11.SA','SBSP3.SA','SMLE3.SA','SUZB5.SA','TBLE3.SA','TIMP3.SA','UGPA3.SA','USIM5.SA','VALE3.SA','VALE5.SA','VIVT4.SA']