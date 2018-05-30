""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants

def buildOrders(ib, action, quantity, price, stop):

    parentId = ib.client.getReqId()

    entryPrice = price + config.ENTRY_SPREAD

    #Entry Order
    entryOrder = Order(
        action = action,
        orderType = "STP",
        auxPrice = entryPrice,
        lmtPrice = 0,
        faProfile = config.ALLOCATION_PROFILE,
        totalQuantity = quantity,
        orderId = parentId,
        transmit = False
    )

    if action == "BUY":
        bracketAction = "SELL"
        profitPrice = entryPrice + config.PROFIT_SPREAD
        lossPrice = entryPrice - stop
    else:
        bracketAction = "BUY"
        profitPrice = entryPrice - config.PROFIT_SPREAD
        lossPrice = entryPrice + stop

    #Profit Order
    profitOrder = Order(
        action = bracketAction,
        orderType = "LMT",
        auxPrice = 0,
        lmtPrice = profitPrice,
        faProfile = config.ALLOCATION_PROFILE,
        totalQuantity = quantity,
        orderId = ib.client.getReqId(),
        parentId = parentId,
        transmit = False
    )

    #Stop Loss Order
    lossOrder = Order(
        action = bracketAction,
        orderType = "STP",
        auxPrice = lossPrice,
        lmtPrice = 0,
        faProfile = config.ALLOCATION_PROFILE,
        totalQuantity = quantity,
        orderId = ib.client.getReqId(),
        parentId = parentId,
        transmit = True
    )

    return [entryOrder, profitOrder, lossOrder]