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

########## CLASS DEFINITON ##########
class AppLogic(threading.Thread):
    """ Thread to Hold Algorithm Logic """
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.name = "Logic"
        self.future = None

########## MAIN ALGO LOGIC  ##########
    def run(self):
        console().info("Staring Second30 App Logic...")

        console().info("Setting Market Data Type : {}".format(config.DATATYPE))
        self.client.reqMarketDataType(MARKET_DATA_TYPES[config.DATATYPE])

        getContractDetails(self.client)
        waitForProp(self, "future")
        today = TradingDay(self.future)

        requests.subscribePriceData(self.client, self.future)

        while True:
            sleep(0.05) # Reduce Processor Load.
            future = self.future
            updateFuture(self.client, future)
            today = updateToday(today)

            #Sleep on Non-Trading Days
            if not today.normalDay: continue

            #Wait for 30 after Open
            while not today.is30AfterOpen(): continue

            if not today.highLow:
                today.highLow = requests.getDailyHighLow(self.client, self.future)

            if today.is10BeforeClose():
                pass #Close Open Orders
