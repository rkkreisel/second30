""" Create and Transmit Orders """
from ib_insync.order import Order
import config
import constants

def buildOrders(action, quantity, price, stop):

    #Entry Order
    entryOrder = Order(
        action = action,
        orderType = "STP",
        auxPrice = price,
        lmtPrice = 0,
        faProfile = config.ALLOCATION_PROFILE,
        faMethod = constants.FA_PROFILE_SHARES,
        totalQuantity = quantity,
        transmit = False
    )

    if action == "BUY":
        bracketAction = "SELL"
        profitPrice = price + config.PROFIT_SPREAD
        lossPrice = price - config.PROFIT_SPREAD
    else:
        bracketAction = "BUY"
        profitPrice = price - config.PROFIT_SPREAD
        lossPrice = price + config.PROFIT_SPREAD

    #Profit Order
    profitOrder = Order(
        action = bracketAction,
        orderType = "LMT",
        auxPrice = 0,
        lmtPrice = profitPrice,
        faProfile = config.ALLOCATION_PROFILE,
        faMethod = constants.FA_PROFILE_SHARES,
        totalQuantity = quantity,
        transmit = False
    )

    #Stop Loss Order
    lossOrder = Order(
        action = bracketAction,
        orderType = "STP",
        auxPrice = lossPrice,
        lmtPrice = 0,
        faProfile = config.ALLOCATION_PROFILE,
        faMethod = constants.FA_PROFILE_SHARES,
        totalQuantity = quantity,
        transmit = True
    )

    return [entryOrder, profitOrder, lossOrder]