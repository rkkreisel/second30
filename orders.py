""" Create and Transmit Orders """
########## STDLIB IMPORTS ##########
from ibapi.order import Order
########## CUSTOM IMPORTS ##########
from logger import getConsole as console
import config

########## CLASS DEFINITION ##########

class BracketOrder():
    """ Bracket Order Creation and Transmission """
    def __init__(self, client, contract, action, account, price):
        self.contract = contract
        self.account = account
        if action != "BUY" and action != "SELL":
            raise ValueError("Bad Action Value: {}".format(action))

        orders = self.buildOrders(action, price)
        self.placeOrders(client, orders)
        client.reqOpenOrders()

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

    def buildOrders(self, action, price):
        """ Create Bracket Order with Entry/Profit/Loss """
        console().info(
            "Creating a Bracket Order to {} {}".format(action, self.contract.localSymbol)
        )

        #Entry Order for High/Low Crossover
        entryOrder = Order()
        entryOrder.orderId = self.account.getOrderId()
        entryOrder.account = self.account.account
        entryOrder.action = action
        entryOrder.orderType = "MIT"
        entryOrder.totalQuantity = config.NUM_CONTRACTS
        entryOrder.auxPrice = price
        entryOrder.lmtPrice = 0
        entryOrder.transmit = False

        #Profit Limit
        profitOrder = Order()
        profitOrder.orderId = self.account.getOrderId()
        profitOrder.action = "SELL" if action == "BUY" else "BUY"
        profitOrder.orderType = "LMT"
        profitOrder.totalQuantity = config.NUM_CONTRACTS
        profitLimit = config.PROFIT_SPREAD if action == "BUY" else -config.PROFIT_SPREAD
        profitOrder.lmtPrice = price + profitLimit
        profitOrder.auxPrice = 0
        profitOrder.parentId = entryOrder.orderId
        profitOrder.transmit = False

        #Loss Limit
        lossOrder = Order()
        lossOrder.orderId = self.account.getOrderId()
        lossOrder.action = "SELL" if action == "BUY" else "BUY"
        lossOrder.orderType = "STP"
        lossOrder.totalQuantity = config.NUM_CONTRACTS
        lossLimit = config.STOP_SPREAD if action == "SELL" else -config.STOP_SPREAD
        lossOrder.auxPrice = price + lossLimit
        lossOrder.lmtPrice = 0
        lossOrder.parentId = entryOrder.orderId
        lossOrder.transmit = True

        return [entryOrder, profitOrder, lossOrder]
