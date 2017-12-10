from ibapi import *
import logging 

from ibapi import wrapper
from ibapi.utils import iswrapper
from ibapi.contract import *
from ibapi.common import *
from ibapi.ticktype import *
from ibapi.execution import *

from applogic import AppLogic

import config

class AppWrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)
        self.console = logging.getLogger("console")
        self.started = False
        self.logic = AppLogic(self)
            
    @iswrapper
    def connectAck(self):
        if self.async:
            self.startApi()
            
    @iswrapper
    def position(self, account:str, contract:Contract, position:float, avgCost:float):
        super().position(account, contract, position, avgCost)
        if contract.symbol == config.SYMBOL:
            self.console.info("Received Pre-Existing Position: {}".format(contract.symbol))
    
    @iswrapper
    def positionEnd(self):
        super().positionEnd()
        self.console.info("End of Position List")

    @iswrapper
    def managedAccounts(self, accountsList:str):
        super().managedAccounts(accountsList)
        self.console.info("Received Accounts  List: {}".format(accountsList))
        self.account = accountsList.split(",")[0]
        self.logic.account = self.account
        
    @iswrapper 
    def nextValidId(self, orderId:int):
        super().nextValidId(orderId)
        self.console.info("Next Valid Order ID: {}".format(str(orderId)))
        self.logic.nextOrderId = orderId
        if not self.started:
            self.logic.start()
            self.started = True
    
    @iswrapper
    def contractDetails(self, reqId:int, contractDetails:ContractDetails):
        super().contractDetails(reqId, contractDetails)
        if reqId == self.logic.stockReqId:
            self.logic.stock = contractDetails
            
    @iswrapper        
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)

        if reqId == self.logic.subscription and tickType == 68: 
            self.logic.price = price
                    
    @iswrapper
    def currentTime(self, time):
        self.logic.update_time_skew(time)
        
        
    @iswrapper
    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        super().execDetails(reqId, contract, execution)
        self.console.info("[Order ID: {}] Trade Executed. {} {} {} @ ${}".format(execution.orderId, execution.side, execution.shares, contract.symbol, execution.price))
        
        if execution.orderId in self.logic.openOrderIds:
            self.console.info("Bracket Order Completed.")
            self.logic.openOrderIds = []
    
    
    