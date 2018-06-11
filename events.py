"""
    Second30 Event Handlers
"""
from logger import getLogger
from ib_insync.order import Trade

log = getLogger()

def registerEvents(ib):
    ib.connectedEvent += connectEvent
    ib.disconnectedEvent += disconnectedEvent
    ib.orderStatusEvent += orderStatus

def connectEvent():
    log.info("Connected.")

def disconnectedEvent():
    log.info("Disconnected from TWS.")

def orderStatus(trade: Trade):
    order = trade.order
    price = order.auxPrice if order.auxPrice > 0 else order.lmtPrice
    orderDetails = "{:<4} {} {} @ ${:<8} ".format(order.action, trade.contract.localSymbol, order.orderType, price)

    log.info("Order: {} Status: {}".format(orderDetails,trade.orderStatus.status))