from ibapi.common import UNSET_DOUBLE
from ibapi.order import *

import config
import logging

class BracketOrder():
    def __init__(self, orderId, account, contract, action, price):
        self.contract = contract
        if action != "BUY" and action != "SELL":
            raise ValueError("Bad Action Value: {}".format(action))
        
        self.create_bracket_order(orderId, account, contract, action, config.SHARE_SIZE, price)
        self.console = logging.getLogger(name="console")


    def create_bracket_order(self, orderid, account, contract, action, quantity, price):
                
        #Main Order
        parent = Order()
        parent.orderId = orderid
        parent.account = account
        parent.action = action
        parent.orderType = "MKT"
        parent.totalQuantity = quantity
        parent.lmtPrice = price
        parent.transmit = False
        parent.OrderRef = config.OrderRef
    
        profit_limit = Order()
        profit_limit.orderId = parent.orderId + 1
        profit_limit.action = "SELL" if action == "BUY" else "BUY"
        profit_limit.orderType = "LMT"
        profit_limit.totalQuantity = quantity
        profit_limit.lmtPrice = price + config.stop_spread if action == "BUY" else price - config.stop_spread
        profit_limit.parentId = parent.orderId
        profit_limit.transmit = False
        parent.OrderRef = config.OrderRef

        stop_limit = Order()
        stop_limit.orderId = parent.orderId + 2
        stop_limit.action = "SELL" if action == "BUY" else "BUY"
        stop_limit.orderType = "STP"
        
        stop_limit.auxPrice = price - config.PRICE_SPREAD if action == "BUY" else price + config.PRICE_SPREAD
        stop_limit.totalQuantity = quantity
        stop_limit.parentId = parent.orderId
        stop_limit.transmit = True
        parent.OrderRef = config.OrderRef

        bracketOrder = []
        bracketOrder.append(parent)
        bracketOrder.append(profit_limit)
        bracketOrder.append(stop_limit)
        self.bracketOrder = bracketOrder
        
    def transmit(self, client):
        for order in self.bracketOrder:
            client.placeOrder(order.orderId, self.contract, order)
            if order.parentId == 0:
                self.console.info("Placing Bracket Order: [ Main Order ] {} {} @ ${} ".format(order.action, order.orderType, order.lmtPrice))
            else:   
                if order.lmtPrice == UNSET_DOUBLE:
                    order_price = order.auxPrice
                else:
                    order_price = order.lmtPrice
                self.console.info("Placing Bracket Order: [ Bracket Order ] {} {} @ ${} ".format(order.action, order.orderType, order_price))

        client.reqIds(0) #Get next valid order id
        return [self.bracketOrder[1].orderId, self.bracketOrder[2].orderId ]
