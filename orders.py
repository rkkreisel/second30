""" Create and Transmit Orders """
########## STDLIB IMPORTS ##########
from ibapi.order import Order
########## CUSTOM IMPORTS ##########
from logger import getConsole as console
import config
import constants

########## CLASS DEFINITION ##########

class BracketOrder():
    """ Bracket Order Creation and Transmission """
    def __init__(self, client, contract, quantity, action, account, price, stop):
        self.contract = contract
        self.account = account
        self.stopPrice = stop
        if action != "BUY" and action != "SELL":
            raise ValueError("Bad Action Value: {}".format(action))

        orders = self.buildOrders(action, price, quantity)
        self.placeOrders(client, orders)
        client.reqOpenOrders()

        self.entryOrder = orders[0]

    def placeOrders(self, client, orders):
        """ Transmit Orders to IB """
        for order in orders:
            price = order.auxPrice if order.auxPrice != 0 else order.lmtPrice
            msg = "Placing Order: {} {} {} @ {} ${:.2f}".format(
                order.action, order.totalQuantity, self.contract.localSymbol,
                order.orderType, price
            )
            console().info(msg)
            client.placeOrder(order.orderId, self.contract, order)

    def buildOrders(self, action, price, quantity):
        """ Create Bracket Order with Entry/Profit/Loss """
        console().info(
            "Creating a Bracket Order to {} {}".format(action, self.contract.localSymbol)
        )

        if action == "BUY":
            entryPrice = price + config.ENTRY_SPREAD
            profitPrice = entryPrice + config.PROFIT_SPREAD
            lossPrice = entryPrice - self.stopPrice
            bracketAction = "SELL"
        else:
            entryPrice = price - config.ENTRY_SPREAD
            profitPrice = entryPrice - config.PROFIT_SPREAD
            lossPrice = entryPrice + self.stopPrice
            bracketAction = "BUY"

        #Entry Order for High/Low Crossover
        entryOrder = Order()
        entryOrder.orderId = self.account.getOrderId()
        entryOrder.account = self.account.account
        entryOrder.action = action
        entryOrder.orderType = "STP"
        entryOrder.auxPrice = entryPrice
        entryOrder.lmtPrice = 0

        if config.ENABLE_MANAGED:
            entryOrder.faProfile = config.ALLOCATION_PROFILE
            entryOrder.faMethod = constants.FA_PROFILE_SHARES

        entryOrder.totalQuantity = quantity
        entryOrder.transmit = False

        #Profit Limit
        profitOrder = Order()
        profitOrder.orderId = self.account.getOrderId()
        profitOrder.action = bracketAction
        profitOrder.orderType = "LMT"
        profitOrder.totalQuantity = config.NUM_CONTRACTS
        profitOrder.lmtPrice = profitPrice
        profitOrder.auxPrice = 0
        profitOrder.parentId = entryOrder.orderId

        if config.ENABLE_MANAGED:
            profitOrder.faProfile = config.ALLOCATION_PROFILE
      
        profitOrder.totalQuantity = quantity
        profitOrder.transmit = False

        #Loss Limit
        lossOrder = Order()
        lossOrder.orderId = self.account.getOrderId()
        lossOrder.action = bracketAction
        lossOrder.orderType = "STP"
        lossOrder.totalQuantity = config.NUM_CONTRACTS
        lossOrder.auxPrice = lossPrice
        lossOrder.lmtPrice = 0
        lossOrder.parentId = entryOrder.orderId

        if config.ENABLE_MANAGED:
            lossOrder.faProfile = config.ALLOCATION_PROFILE

        lossOrder.totalQuantity = quantity
        lossOrder.transmit = True

        return [entryOrder, profitOrder, lossOrder]

def logOrder(ledger, orderId, symbol, order, newStatus, oldStatus):
    """ Log Order Status to CSV and Console if the State has Changed """
    price = order.auxPrice if order.auxPrice != 0 else order.lmtPrice
    action, quantity, orderType = order.action, order.totalQuantity, order.orderType

    orderMsg = "{} {} {} @ {} ${:.2f}".format(action, quantity, symbol, orderType, price)
    msg = "ID: {} Status: [{}]: {}".format(orderId, orderMsg, newStatus)
    if oldStatus != newStatus:
        if newStatus not in ["PendingSubmit", "PreSubmitted"]:
            console().info(msg)
        ledger.log(orderId, symbol, action, orderType, quantity, price, newStatus)
