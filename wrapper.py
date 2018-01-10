""" Callback Functions from TWS Gateway / Workstation """

########## STDLIB IMPORTS ##########

########## CUSTOM IMPORTS ##########

from ibapi import wrapper
from ibapi.utils import iswrapper

from logic import AppLogic
from logger import getConsole as console

from account import Account
from helpers import waitForProp

########## CLASS DEFINITON ##########
class AppWrapper(wrapper.EWrapper):
    """ Thread to Manage Callbacks. """
    def __init__(self):
        wrapper.EWrapper.__init__(self)
        self.startedLogic = False
        self.logic = AppLogic(self)

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

    @iswrapper
    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)
        symbol = contractDetails.summary.localSymbol
        expires = contractDetails.summary.lastTradeDateOrContractMonth
        console().info("Received Contract Details for: {}. Expires: {}".format(symbol, expires))
        self.logic.client.pushRequestData(reqId, {symbol : contractDetails})

    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)
        console().info("Got All Contract Details.")
        self.logic.client.finishRequest(reqId)
