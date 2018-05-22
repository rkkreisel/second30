"""
    Second30 Algorithm Logic
"""
import logging
from datetime import time, date, datetime
from sys import exit as sysexit
from ib_insync import IB
from ib_insync.contract import ContFuture, Contract, Future

import constants
import config
import helpers
import orders

class Algo():
    """ Second30 Algorithm class """
    def __init__(self, ib: IB):
        self.ib = ib

    def run(self):
        """ Execute the algorithm """
        contract = self.get_contract()
        tradeContract = self.ib.qualifyContracts(contract.contract)[0]
        quantity = helpers.parseAdvisorConfig(self.ib.requestFA(constants.FA_PROFILES))

        open_today = helpers.is_open_today(contract)
        if not open_today:
            logging.error("Today is not a valid trading day")
            sysexit()
        logging.info("Today is a valid trading day.")

        logging.info("Waiting for Opening Bell")
        self.ib.waitUntil(time(hour=9,minute=30))
        logging.info("After market open @ 9:30")

        #Wait for Historic Data
        logging.info("Waiting for 10AM")
        self.ib.waitUntil(time(hour=10))
        logging.info("After 10 AM")

        high, low = self.get_high_low(contract)
        logging.info("Got High: ${} and Low: ${}".format(high,low))

        #Check HiLo Spread
        spread = float("{:.4f}".format((float(high) - float(low)) / float(low)))
        if spread > config.HIGH_LOW_SPREAD_RATIO:
            logging.info("Spread Ratio: {:.4f} above threshold: {}. Invalid Day".format(spread, config.HIGH_LOW_SPREAD_RATIO))
            return
        else:
            logging.info("Spread Ratio: {:.4f} below threshold: {}. Valid Day".format(spread,config.HIGH_LOW_SPREAD_RATIO))

         #Calculate Stop
        spreadDiff = round(float("{:.2f}".format((float(high) - float(low)) / 2.0))*4) / 4 
        stop = spreadDiff if spreadDiff > config.STOP_SPREAD else  config.STOP_SPREAD
        logging.info("Calculated Stop Spread: ${}".format(stop))

        highBracket = orders.buildOrders("BUY", quantity, high, stop)
        lowBracket = orders.buildOrders("SELL", quantity, low, stop)
        
        for order in highBracket:
            self.ib.placeOrder(tradeContract, order)
        for order in lowBracket:
            self.ib.placeOrder(tradeContract, order)

        for trade in self.ib.trades():
            while not trade.isDone():
                self.ib.waitOnUpdate()

    def get_contract(self):
        """ Get the current futures symbol details """
        contract = self.ib.reqContractDetails(
            ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
        )
        if not contract:
            logging.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
            sysexit()
        else:
            return contract[0]

    def get_high_low(self, contract: Contract):
        """ Get highest and lowest price during first 30 mins of trading """
        today = date.today()
        end_time = datetime(year=today.year, month=today.month, day=today.day, hour=10)

        data = self.ib.reqHistoricalData(
            contract=contract.contract,
            endDateTime=end_time,
            durationStr="1800 S",
            barSizeSetting="30 mins",
            whatToShow="TRADES",
            useRTH=True
        )

        return data[0].high, data[0].low