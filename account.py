""" Manages Account Information Received from IB """
########## STDLIB IMPORTS ##########
import xml.etree.ElementTree as ET

########## CUSTOM IMPORTS ##########
from logger import getConsole as console
import config
########## CLASS DEFINITON ##########
class Account():
    """ Account Information with Position and Order ID Data"""
    def __init__(self):
        self.account = None
        self._nextOrderId = None
        self.positions = {}
        self.openOrders = {}
        self.tmpOrders = {}


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

    def setAccount(self, accountString):
        """ Parse Comma Separated Account List from IB """
        accounts = accountString.split(",")
        if len(accounts) > 1:
            console().error("Received More than One Account. Not Implemented.")
        self.account = accounts[0]

    def updatePosition(self, contract, position):
        """ Add a New Position to the Account """
        key = contract.localSymbol
        if key in list(self.positions.keys()) and position == 0:
            self.positions.pop(key)
        if position != 0:
            self.positions[key] = (contract, position)

def parseAdvisorConfig(xml):
    """ Get # Of Contracts from Current Advisor Profile """
    root = ET.fromstring(xml)
    profileTag = None
    for profile in  root.getchildren():
        for attrib in profile.getchildren():
            if attrib.tag == 'name':
                if attrib.text.lower() == config.ALLOCATION_PROFILE.lower():
                   profileTag = profile
    if not profileTag: return None

    allocations = None
    for attrib in profileTag.getchildren():
        if attrib.tag == "ListOfAllocations":
            allocations = attrib
    if not allocations: return None 
    
    amount = 0
    for allocation in allocations.getchildren():
        for attrib in allocation:
             if attrib.tag == "amount":
                 amount += int(float(attrib.text))
    return amount