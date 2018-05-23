""" Algorithm Requests for Data from IBAPI """
########## STDLIB IMPORTS ##########
from datetime import datetime, date

########## CUSTOM IMPORTS ##########
from logger import getConsole as console
import config
import constants 

########## SUBSCRIPTIONS ##########
def subscribePriceData(client, future):
    """ Start Current Price Data Subscription """
    name = future.contract.localSymbol
    console().info("Requesting a Price Data Subscription For: {}".format(name))
    return client.subscribe(
        name="{} {} Price Data".format(name, config.DATATYPE),
        startFunc=client.reqMktData,
        startArgs=[client.REQUEST_ID, future.contract, "", False, False, None],
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

def getFirst30HighLow(client, future):
    """ Get the High and Low for the First 30 Mins of Trading """
    console().info("Getting The First 30 High/Low.")

    reqId = client.startRequest()

    today = date.today()
    endTime = datetime(year=today.year, month=today.month, day=today.day, hour=10)
    endTime = endTime.strftime("%Y%m%d %H:%M:%S")

    client.pushRequestData(reqId, {"name" : "HIGH/LOW"})
    client.reqHistoricalData(
        reqId, future.contract, endTime, "1800 S", "30 mins", "TRADES", 1, 1, False, []
    )
    return client.waitForRequest(reqId, purge=True)["historical"]

def getFullDayHighLow(client, future):
    """ Get the High and Low for The Entire Day """
    reqId = client.startRequest()

    now = datetime.now()
    delta = now - datetime(year=now.year, month=now.month, day=now.day, hour=9, minute=30)
    duration = "{} S".format(delta.seconds)

    client.pushRequestData(reqId, {"name" : "FULL DAY HIGH/LOW"})
    client.reqHistoricalData(
        reqId, future.contract, "", duration, "1 day", "TRADES", 1, 1, False, []
    )
    return client.waitForRequest(reqId, purge=True)["historical"]

def getAdvisorConfig(client):
    """Get the XML Configuration for the Advisor Profile """
    console().info("Getting Advisor Profile Config.")
    reqId = client.startRequest()
    
    client.pushRequestData(reqId, {"name" : "ADVISOR CONFIG"})
    client.requestFA(constants.FA_PROFILES)
    return client.waitForRequest(reqId, purge=True)["xml"]

########## DATA REQUESTS ##########
