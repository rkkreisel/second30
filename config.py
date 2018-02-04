""" Second30 Configuration Values """

########## CONFIGURATION ##########

VERSION = "0.1"
LOGFILE = "second30.log"
LEDGERFILE = "second30_trades.csv"

HOST = "localhost"
PORT = 55555
CLIENTID = 1

ENTRY_SPREAD = 0.25
PROFIT_SPREAD = 1.00
STOP_SPREAD = 3.00
NUM_CONTRACTS = 1

SYMBOL = "ES"
EXCHANGE = "GLOBEX"

#Normal Timezone is CST.
NORMAL_TRADING_HOURS = "1700-1515,1530-1600"

# Type of Market Data To Stream. (LIVE, DELAYED, FROZEN_DELAYED)
DATATYPE = "LIVE"
