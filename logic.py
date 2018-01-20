""" Trading Algorithm Definition """

########## STDLIB IMPORTS ##########
import threading

########## CUSTOM IMPORTS ##########
from logger import getConsole as console

from contracts import getContractDetails, getCurrentFuturesContract
from tradingday import TradingDay, updateTradingDay

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

        future = getCurrentFuturesContract(getContractDetails(self.client))
        today = TradingDay(future)

        while True:
            today = updateTradingDay(today)

            #Sleep on Non-Trading Days
            if not today.isNormalTradingDay(): continue


       