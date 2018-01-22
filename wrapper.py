""" Callback Functions from TWS Gateway / Workstation """

########## STDLIB IMPORTS ##########

########## CUSTOM IMPORTS ##########

from ibapi import wrapper
from ibapi.utils import iswrapper

from logic import AppLogic
from logger import getConsole as console
from account import Account
from helpers import waitForProp
from constants import TICK_TYPES
from requests import subscribeAccountPositions

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
        console().info("[{},{}] API Message: {}".format(reqId, errorCode, errorString))

    @iswrapper
    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        if account == self.logic.account.account:
            console().info("Position Update: {}: #Contracts: {}".format(contract.localSymbol, position))
            self.logic.account.updatePosition(contract, position)
        else:
            console().warning("Got Position for Untracked Account: {}".format(account))
