""" Second30 Configuration Values """

########## CUSTOM IMPORTS ##########
from constants import *

########## CONFIGURATION ##########

VERSION = "0.1"
LOGFILE = "second30.log"

HOST = "localhost"
PORT = 55555
CLIENTID = 1

SHARE_SIZE = 1
BUY_SPREAD = 1
STOP_SPREAD = .75

SYMBOL = "ES"
EXCHANGE = "GLOBEX"

#Normal Timezone is CST.
NORMAL_TRADING_HOURS = "1700-1515,1530-1600"

# Type of Market Data To Stream. (LIVE, DELAYED, FROZEN_DELAYED)
DATATYPE = "FROZEN_DELAYED"
