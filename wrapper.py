""" Callback Functions from TWS Gateway / Workstation """

########## STDLIB IMPORTS ##########

########## CUSTOM IMPORTS ##########

from ibapi import wrapper
from ibapi.utils import iswrapper

from logic import AppLogic
from logger import getConsole as console
from constants import TICK_TYPES
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
        self.logic.account.setNextOrderId(orderId)
        console().info("Next Order ID: {}".format(orderId))
        if not self.startedLogic:
            self.logic.start()
            self.startedLogic = True

    @iswrapper
    def managedAccounts(self, accountsList):
        self.logic.account.setAccount(accountsList)
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
        price = order.auxPrice if order.auxPrice != 0 else order.lmtPrice
        orderMsg = "{} {} {} @ {} ${:.2f}".format(
            order.action, order.totalQuantity, contract.localSymbol, order.orderType, price
        )
        if orderId not in self.logic.account.openOrders.keys():
            console().info("ID: {}: [{}]: {}".format(orderId, orderMsg, orderState.status))
        self.logic.account.tmpOrders[orderId] = (contract, order, orderState.status)

    @iswrapper
    def openOrderEnd(self):
        self.logic.account.openOrders = self.logic.account.tmpOrders
        self.logic.account.tmpOrders = {}

    @iswrapper
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld):
        try:
            data = self.logic.account.openOrders[orderId]
            contract, order, oldStatus = data[0].localSymbol, data[1], data[2]
            price = order.auxPrice if order.auxPrice != 0 else order.lmtPrice
            orderMsg = "{} {} {} @ {} ${:.2f}".format(
                order.action, order.totalQuantity, contract, order.orderType, price
            )
            self.logic.account.openOrders[orderId] = (data[0], data[1], status)
        except (KeyError, AttributeError):
            contract, orderMsg, oldStatus = "?", "?", status

        if status in ["Cancelled", "Filled"]:
            self.client.reqOpenOrders()

        if oldStatus != status:
            console().info("ID: {} Status: [{}]: {}".format(orderId, orderMsg, status))

def apiMessage(msg):
    """ Print API Messages """
    msg = msg.replace("\n", ". ")
    console().info("API: {}".format(msg))
