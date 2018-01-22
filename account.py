""" Manages Account Information Received from IB """
########## STDLIB IMPORTS ##########

########## CUSTOM IMPORTS ##########
from logger import getConsole as console

########## CLASS DEFINITON ##########
class Account():
    """ Account Information with Position and Order ID Data"""
    def __init__(self, accountString):
        self.account = parseAccountString(accountString)
        self._nextOrderId = None
        self.positions = {}


    def __repr__(self):
        return self.account

    def setNextOrderId(self, orderId):
        """ Set the Next Order ID sent by IB """
        self._nextOrderId = orderId

    def getOrderId(self):
        """ Get the next Order ID and Increment """
        if self._nextOrderId is None:
            raise ValueError("Missing a Valid Order ID")
        orderId = self._nextOrderId
        self._nextOrderId += 1
        return orderId

    def updatePosition(self, contract, position):
        """ Add a New Position to the Account """
        key = contract.localSymbol
        if key in list(self.positions.keys()) and position == 0:
            self.positions.pop(key)
        if position != 0:
            self.positions[key] = (contract, position)

########## FUNCTIONS ##########
def parseAccountString(accountString):
    """ Parse Comma Separated Account List from IB """
    accounts = accountString.split(",")
    if len(accounts) > 1:
        console().error("Received More than One Account. Not Implemented.")
    return accounts[0]
