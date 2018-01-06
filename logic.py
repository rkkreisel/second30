import datetime
import logging
import threading
import time

from ibapi import *
from ibapi.contract import *
import config
from tradingday import TradingDay
from bracketorder import BracketOrder

class AppLogic(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.daemon = True
        self.app = app
        self.name = "AppLogic"
        self.console = logging.getLogger("console")
        self.nextReqId = 5000
        self.account = None

        self.stock = None
        self.stockReqId = None

        self.serverTime = None
        self.tradingDay = None
        self.timeSkew = 0

        self.subscription = None

        self.price = None
        self.waitCrossover = False

        self.nextOrderId = None
        self.openOrderIds = []

    # Ran After First Order ID.
    def run(self):

        self.stockReqId = self.gen_req_id()
        stock_contract = self.gen_contract()
        self.console.info("Requesting Details for Symbol: {}".format(stock_contract.symbol))
        self.get_stock_details(self.stockReqId, stock_contract)

        self.wait_for("stock")
        self.console.info("Got Details for: {}".format(self.stock.longName))

        self.tradingDay = TradingDay(self.stock.liquidHours)
        self.get_time_skew()
        self.tradingDay.skew = self.timeSkew

        while True:
            if int(time.time()) % 60 == 0:
                self.get_time_skew()

            if datetime.date.today() != self.tradingDay.today:
                self.tradingDay = TradingDay(self.stock.liquidHours)

            if not self.tradingDay.openToday:
                self.console.info("Market Not Open Today. Sleeping Until Tomorrow.")
                while datetime.date.today() == self.tradingDay.today:
                    pass
                self.get_time_skew()
                continue

            if datetime.datetime.today() < self.tradingDay.open_time:
                self.console.info("The Market Is Currently: CLOSED")
                self.console.info("Waiting for Market to Open")
                while datetime.datetime.today() < self.tradingDay.open_time:
                    pass
                self.get_time_skew()

            if datetime.datetime.today() > self.tradingDay.close_time:
                self.console.info("The Market Is Currently: CLOSED")
                self.console.info("Market Closed For the Day. Sleeping Until Tomorrow")
                while datetime.date.today() == self.tradingDay.today:
                    pass
                self.get_time_skew()
                continue

            while self.tradingDay.is_market_open():
                self.console.info("The Market Is Currently: OPEN")
                if self.subscription is None:
                    self.console.info("Subscribing to Market Data for {}".format(self.stock.longName))
                    self.subscribe(stock_contract)
                    self.console.info("[{}] Waiting for Price Data...".format(self.stock.longName))
                    while self.price == None:
                        pass
                if self.tradingDay.is_30_after_open():
                    if self.tradingDay.is_highlow_set():
                        while not self.tradingDay.is_10_before_close():
                            if not self.isOrderOpen() and not self.waitingforCrossOver():
                                if self.price > self.tradingDay.high:
                                    order = BracketOrder(self.nextOrderId, self.account, self.gen_contract(), "BUY",
                                                         self.price)
                                    self.openOrderIds = order.transmit(self.app)
                                    self.waitCrossover = True
                                elif self.price < self.tradingDay.low:
                                    order = BracketOrder(self.nextOrderId, self.account, self.gen_contract(), "SELL",
                                                         self.price)
                                    self.openOrderIds = order.transmit(self.app)
                                    self.waitCrossover = True
                            else:  # Waiting for Order To Finish Execution
                                continue
                        self.console.info("Closing Out Positions for the day")
                        while self.tradingDay.is_market_open():
                            pass
                    else:
                        self.console.info("Need High Low Data for {}".format(self.tradingDay.todayString))
                        self.print_current()
                        self.tradingDay.prompt_highlow()
                        self.console.info("Set Daily High: ${} and Daily Low: ${}"
                                          .format(self.tradingDay.high, self.tradingDay.low))
                else:
                    self.console.info("Waiting for 30 Minutes of Trading Data")
                    while not self.tradingDay.is_30_after_open():
                        pass

    def waitingforCrossOver(self):
        if self.waitCrossover:
            return True

        if self.price < self.tradingDay.high and self.price > self.tradingDay.low:
            self.waitCrossover = False

    def print_current(self):
        self.console.info("[{}] Current Price: ${}".format(self.stock.longName, self.price))

    def gen_contract(self):
        contract = Contract()
        contract.symbol = config.Symbol
        contract.secType = config.secType
        contract.currency = "USD"
        contract.exchange = config.exchange
        contract.localSymbol = config.LocalSymbol
        return contract

    def get_stock_details(self, req_id, contract):
        self.app.reqContractDetails(req_id, contract)

    def gen_req_id(self):
        req_id = self.nextReqId
        self.nextReqId += 1
        return req_id

    def wait_for(self, objname):
        while getattr(self, objname) is None:
            pass

    def get_time_skew(self):
        self.console.info("Requesting Server Time")
        self.app.reqCurrentTime()

        while self.serverTime is None:
            pass

    def update_time_skew(self, serverTime):
        self.serverTime = serverTime

        skew = int(time.time()) - self.serverTime

        # Give a 2 Second Buffer
        if skew > 0 and skew > 2:
            self.timeSkew = skew
        elif skew < 0 and skew < -2:
            self.timeSkew = skew
        else:
            self.timeSkew = 0

        self.tradingDay.skew = self.timeSkew

        self.console.info("Local Time is {} seconds ahead of Server Time".format(self.timeSkew))

    def subscribe(self, stock):
        self.subscription = self.gen_req_id()
        self.app.reqMarketDataType(3)
        self.app.reqMktData(self.subscription, stock, "", False, False, None)

    def isOrderOpen(self):
        if len(self.openOrderIds) > 0:
            return True
        return False