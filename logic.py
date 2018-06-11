"""
    Second30 Algorithm Logic
"""
import logger
from datetime import time, date, datetime
from sys import exit as sysexit
from ib_insync import IB
from ib_insync.contract import ContFuture, Contract, Future

log = logger.getLogger()

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
        log.info("Got Trading Contract: {}".format(tradeContract.localSymbol))
        quantity = helpers.parseAdvisorConfig(self.ib.requestFA(constants.FA_PROFILES))
        log.info("Got Quanity from Advisor Profile {}:{}".format(config.ALLOCATION_PROFILE, quantity))

        open_today = helpers.is_open_today(contract)
        if not open_today:
            log.error("Today is not a valid trading day")
            sysexit()
        log.info("Today is a valid trading day.")

        log.info("Waiting for Opening Bell")
        self.ib.waitUntil(time(hour=9,minute=30))
        log.info("After market open @ 9:30")

        #Wait for Historic Data
        log.info("Waiting for 10AM")
        self.ib.waitUntil(time(hour=10))
        log.info("After 10 AM")

        high, low = self.get_high_low(contract)
        log.info("Got High: ${} and Low: ${}".format(high,low))

        #Check HiLo Spread
        spread = float("{:.4f}".format((float(high) - float(low)) / float(low)))
        if spread > config.HIGH_LOW_SPREAD_RATIO:
            log.info("Spread Ratio: {:.4f} above threshold: {}. Invalid Day".format(spread, config.HIGH_LOW_SPREAD_RATIO))
            sysexit()
        else:
            log.info("Spread Ratio: {:.4f} below threshold: {}. Valid Day".format(spread,config.HIGH_LOW_SPREAD_RATIO))

         #Calculate Stop
        spreadDiff = round(float("{:.2f}".format((float(high) - float(low)) / 2.0))*4) / 4 
        stop = spreadDiff if spreadDiff > config.STOP_SPREAD else  config.STOP_SPREAD
        log.info("Calculated Stop Spread: ${}".format(stop))

        highBracket = orders.buildOrders(self.ib, "BUY", quantity, high, stop)
        lowBracket = orders.buildOrders(self.ib, "SELL", quantity, low, stop)
        
        log.info("Placing Upper Bracket Orders...")
        for order in highBracket:
            self.ib.placeOrder(tradeContract, order)
            log.info("  Upper: {:<4} {}. TYPE = {} AUX = ${:<8} LMT = ${:<8}".format(order.action, tradeContract.localSymbol, order.orderType, order.auxPrice, order.lmtPrice))
        log.info("Placing Lower Bracket Orders...")
        for order in lowBracket:
            self.ib.placeOrder(tradeContract, order)
            price = order.auxPrice if order.auxPrice > 0 else order.lmtPrice
            log.info("  Lower: {:<4} {}. {} @ ${:<8}".format(order.action, tradeContract.localSymbol, order.orderType, price))

        log.info("")

        for trade in self.ib.trades():
            while not trade.isDone():
                self.ib.waitOnUpdate()

    def get_contract(self):
        """ Get the current futures symbol details """
        contract = self.ib.reqContractDetails(
            ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
        )
        if not contract:
            log.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
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