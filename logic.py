""" Trading Algorithm Definition """

########## STDLIB IMPORTS ##########
import threading
from time import sleep

########## CUSTOM IMPORTS ##########
from logger import getConsole as console
from contracts import getContractDetails, updateFuture
from tradingday import TradingDay, updateToday
import config
from constants import MARKET_DATA_TYPES
import requests
from helpers import waitForProp
from orders import BracketOrder
from account import Account


########## CLASS DEFINITON ##########
class AppLogic(threading.Thread):
    """ Thread to Hold Algorithm Logic """
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.name = "Logic"
        self.future = None
        self.account = Account()

########## MAIN ALGO LOGIC  ##########
    def run(self):
        client = self.client
        console().info("Staring Second30 App Logic...")

        console().info("Setting Market Data Type : {}".format(config.DATATYPE))
        client.reqMarketDataType(MARKET_DATA_TYPES[config.DATATYPE])

        client.reqOpenOrders()

        getContractDetails(client)
        waitForProp(self, "future")
        today = TradingDay(self.future)

        today.executedToday = requests.didAlreadyExecute(client)

        if len(self.account.openOrders):
            today.executedToday = True
            console().info("Found Pending Open Orders for Second30")

        requests.subscribePriceData(client, self.future)

        #BracketOrder(client, self.future.summary, "BUY", self.account, 100.5)

        while True:
            sleep(0.05) # Reduce Processor Load.
            updateFuture(client, self.future)
            today = updateToday(today)

            #Sleep on Non-Trading Days
            if not today.normalDay: continue

            #Wait for 30 after Open
            while not today.is30AfterOpen(): continue

            #Pull HighLow
            if not today.highLow:
                today.highLow = requests.getDailyHighLow(client, self.future)

            if today.is10BeforeClose():
                pass #Close Open Orders
