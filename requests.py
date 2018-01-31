""" Algorithm Requests for Data from IBAPI """
########## STDLIB IMPORTS ##########
from datetime import datetime, date

########## CUSTOM IMPORTS ##########
from logger import getConsole as console
import config
from constants import REQUEST_NAMES
########## SUBSCRIPTIONS ##########
def subscribePriceData(client, future):
    """ Start Current Price Data Subscription """
    name = future.summary.localSymbol
    console().info("Requesting a Price Data Subscription For: {}".format(name))
    return client.subscribe(
        name="{} {} Price Data".format(name, config.DATATYPE),
        startFunc=client.reqMktData,
        startArgs=[client.REQUEST_ID, future.summary, "", False, False, None],
        stopFunc=client.cancelMktData,
        stopArgs=[client.REQUEST_ID],
    )

def subscribeAccountPositions(client):
    """ Subscribe to Updates in Held Positions """
    console().info("Subscribing to Account Position Updates")
    return client.subscribe(
        name="Account Position Updates",
        startFunc=client.reqPositions,
        startArgs=[],
        stopFunc=client.cancelPositions,
        stopArgs=[],
    )

def getDailyHighLow(client, future):
    """ Get the High and Low for the First 30 Mins of Trading """
    console().info("Getting The First 30 High/Low.")

    reqId = client.startRequest()
    today = date.today()
    endTime = datetime(year=today.year, month=today.month, day=today.day, hour=10)
    endTime = endTime.strftime("%Y%m%d %H:%M:%S")
    client.pushRequestData(reqId, {"name" : "HIGH/LOW"})
    client.reqHistoricalData(
        reqId, future.summary, endTime, "1800 S", "30 mins", "TRADES", 1, 1, False, []
    )

    return client.waitForRequest(reqId, purge=True)

def getOpenOrders(client):
    """ Get open orders for the current API Client ID """
    reqId = client.startRequest()
    client.pushRequestData(reqId, {"name": REQUEST_NAMES["ORDERS"]})
    client.reqOpenOrders()
    return client.waitForRequest(reqId, purge=True)

########## DATA REQUESTS ##########
