""" Callback Functions from TWS Gateway / Workstation """

########## STDLIB IMPORTS ##########

########## CUSTOM IMPORTS ##########

from ibapi import wrapper
from ibapi.utils import iswrapper

from logic import AppLogic
from logger import getConsole as console
from account import Account
from helpers import waitForProp
from constants import TICK_TYPES, REQUEST_NAMES
from requests import subscribeAccountPositions
from contracts import getCurrentFuturesContract

########## CLASS DEFINITON ##########
class AppWrapper(wrapper.EWrapper):
    """ Thread to Manage Callbacks. """
    def __init__(self):
        wrapper.EWrapper.__init__(self)
        self.startedLogic = False
        self.logic = AppLogic(self)
        self.client = self.logic.client

    @iswrapper
    def nextValidId(self, orderId):
        waitForProp(self.logic, "account")
        self.logic.account.setNextOrderId(orderId)
        console().info("Next Order ID: {}".format(orderId))
        if not self.startedLogic:
            self.logic.start()
            self.startedLogic = True

    @iswrapper
    def managedAccounts(self, accountsList):
        self.logic.account = Account(accountsList)
        console().info("Received Account: {}".format(self.logic.account))
        subscribeAccountPositions(self.client)

    @iswrapper
    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)
        symbol = contractDetails.summary.localSymbol
        expires = contractDetails.summary.lastTradeDateOrContractMonth
        console().info("Received Contract Details for: {}. Expires: {}".format(symbol, expires))
        self.client.pushRequestData(reqId, {symbol : contractDetails})

    @iswrapper
    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)
        console().info("Got All Contract Details.")
        self.client.finishRequest(reqId)
        contractDetails = self.client.getRequestData(reqId)
        self.client.purgeRequest(reqId)
        self.logic.future = getCurrentFuturesContract(contractDetails)

    @iswrapper
    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        if tickType == TICK_TYPES["LAST_PRICE"]:
            self.client.pushRequestData(reqId, {"price":{"last": price}})

    @iswrapper
    def tickSize(self, reqId, tickType, size):
        super().tickSize(reqId, tickType, size)

    @iswrapper
    def tickGeneric(self, reqId, tickType, value):
        super().tickGeneric(reqId, tickType, value)

    @iswrapper
    def tickString(self, reqId, tickType, value):
        super().tickString(reqId, tickType, value)

    @iswrapper
    def error(self, reqId, errorCode, errorString):
        super().error(reqId, errorCode, errorString)
        apiMessage(errorString)

    @iswrapper
    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        if account == self.logic.account.account:
            console().info("Position Update: {}: #Contracts: {}".format(
                contract.localSymbol, position))
            self.logic.account.updatePosition(contract, position)
        else:
            console().warning("Got Position for Untracked Account: {}".format(account))

    @iswrapper
    def historicalData(self, reqId, bar):
        console().info(
            "Got Historical Data. Date:{}. High:${}. Low:${}".format(bar.date, bar.high, bar.low)
        )
        self.client.pushRequestData(reqId, {"historical": {"high": bar.high, "low": bar.low}})


    @iswrapper
    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        console().info("Got First 30 Data For Today")
        self.client.finishRequest(reqId)

    @iswrapper
    def openOrder(self, orderId, contract, order, orderState):
        console().info("Got Order: {}. {}, {}".format(contract, order, orderState))
        reqId = self.client.getIDByName(REQUEST_NAMES["ORDERS"])
        if reqId:
            self.client.pushRequestData(reqId, {orderId: (contract, order, orderState)})
        else:
            console().error("Failed to Track Open Orders")

    def openOrderEnd(self):
        reqId = self.client.getIDByName(REQUEST_NAMES["ORDERS"])
        if reqId:
            console().info("Got All Open Orders".format())
            self.client.finishRequest(reqId)
        else:
            console().error("Failed to Track Open Orders")

def apiMessage(msg):
    """ Print API Messages """
    console().info("API: {}".format(msg))
