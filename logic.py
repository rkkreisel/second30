""" Trading Algorithm Definition """

########## STDLIB IMPORTS ##########
import threading
from time import sleep

########## CUSTOM IMPORTS ##########
from logger import getConsole as console
from contracts import getContractDetails, updateFuture
from tradingday import TradingDay, updateToday
import config
from constants import MARKET_DATA_TYPES

import requests
from helpers import waitForProp
from orders import BracketOrder
from account import Account, parseAdvisorConfig


########## CLASS DEFINITON ##########
class AppLogic(threading.Thread):
    """ Thread to Hold Algorithm Logic """
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.name = "Logic"
        self.future = None
        self.account = Account()

########## MAIN ALGO LOGIC  ##########
    def run(self):
        client = self.client
        console().info("Staring Second30 App Logic...")

        console().info("Setting Market Data Type : {}".format(config.DATATYPE))
        client.reqMarketDataType(MARKET_DATA_TYPES[config.DATATYPE])

        quantity = config.NUM_CONTRACTS
        if config.ENABLE_MANAGED:
            xml = requests.getAdvisorConfig(client)        
            quantity = parseAdvisorConfig(xml)
            if not quantity:
                console().error("Failed to Parse Advisor Profiles")
                client.interruptHandler()
            console().info("Set Advisor Total Quantity to : {}".format(quantity))

        client.reqOpenOrders()

        getContractDetails(client)
        waitForProp(self, "future")
        today = TradingDay(self.future)
        state = getNewState()

        #Already After 10. Check if Still Valid
        if today.isMarketOpen() and today.is30AfterOpen():
            state = checkMissedExecution(client, self.future, today.normalDay, state)

        while True:
            sleep(.05) # Reduce Processor Load.
            updateFuture(client, self.future)
            newDay = updateToday(today)
            if newDay != today:
                state = getNewState()
            today = newDay

            #Sleep on Non-Trading Days
            if not today.normalDay: continue

            #Wait for Market Open
            while not today.isMarketOpen(): continue

            #Wait for 30 after Open
            while not today.is30AfterOpen(): continue

            #Cancel Unused Bracket if the Other Fired
            if state["executedToday"]:
                state = cancelUnusedBracket(client, state, self.account.openOrders)
                continue

            #Pull HighLow
            if not state["highLow"]:
                console().info("Getting High/Low Data For First 30.")
                state["highLow"] = requests.getFirst30HighLow(client, self.future)

            high, low = state["highLow"]["high"], state["highLow"]["low"] #pylint: disable=unsubscriptable-object

            #Check HiLo Spread
            spread = float("{:.4f}".format((float(high) - float(low)) / float(low)))
            if spread > config.HIGH_LOW_SPREAD_RATIO:
                today.normalDay = False
                console().info("Spread Ratio: {:.4f} above threshold: {}. Invalid Day".format(spread,config.HIGH_LOW_SPREAD_RATIO))
                continue
            else:
                console().info("Spread Ratio: {:.4f} below threshold: {}. Valid Day".format(spread,config.HIGH_LOW_SPREAD_RATIO))

            #Calculate Stop
            spreadDiff = round(float("{:.2f}".format((float(high) - float(low)) / 2.0))*4) / 4 
            stop = spreadDiff if spreadDiff > config.STOP_SPREAD else  config.STOP_SPREAD

            console().info("Calculated Stop Spread: ${}".format(stop))

            #Submit Orders for the Day
            contract = self.future.summary
            state["highBracket"] = BracketOrder(client, contract, quantity, "BUY", self.account, high, stop)
            state["lowBracket"] = BracketOrder(client, contract, quantity, "SELL", self.account, low, stop)
            state["executedToday"] = True

def getNewState():
    """ Generate a Blank State for a New Day """
    return {
        "executedToday" : False,
        "highLow" : None,
        "lowBracket" : None,
        "highBracket" : None
    }

def cancelUnusedBracket(client, state, openOrders):
    """ Remove Other Bracket if it Exists """
    highBracket, lowBracket = state["highBracket"], state["lowBracket"]
    if highBracket is None and lowBracket is None:
        return state

    highOrderId = highBracket.entryOrder.orderId
    lowOrderId = lowBracket.entryOrder.orderId

    if highOrderId not in openOrders.keys():
        client.cancelOrder(lowOrderId)
        console().info("Cancelling the Lower Bracket")
        state["lowBracket"] = None
        state["highBracket"] = None
    elif lowOrderId not in openOrders.keys():
        client.cancelOrder(highOrderId)
        console().info("Cancelling The Upper Bracket")
        state["lowBracket"] = None
        state["highBracket"] = None

    return state

def checkMissedExecution(client, future, normalDay, state):
    """ Check if We've Missed the Second30 Conditions """
    if not normalDay: return state

    first30 = requests.getFirst30HighLow(client, future)
    firstHigh, firstLow = first30["high"], first30["low"]

    allDay = requests.getFullDayHighLow(client, future)
    dayHigh, dayLow = allDay["high"], allDay["low"]

    if dayHigh > firstHigh or dayLow < firstLow:
        state["executedToday"] = True
        console().warning("Already Executed Today or Missed Trading Window. NOT TRADING.")
    return state
