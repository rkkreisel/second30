""" Trading Algorithm Definition """

########## STDLIB IMPORTS ##########
import threading
from datetime import date

########## CUSTOM IMPORTS ##########
from logger import getConsole as console

from contracts import getContractDetails, getCurrentFuturesContract
from tradingday import TradingDay

########## CLASS DEFINITON ##########
class AppLogic(threading.Thread):
    """ Thread to Hold Algorithm Logic """
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.name = "Logic"

    def run(self):
        console().info("Staring Second30 App Logic...")

        futures = getContractDetails(self.client)
        currentFuture = getCurrentFuturesContract(futures)

        today = date.today()
        tradingDay = TradingDay(currentFuture)

        while True:
            if  date.today() != today:
                today = date.today()
                tradingDay = TradingDay(currentFuture)


            