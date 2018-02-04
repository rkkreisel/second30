""" Algorithm Requests for Data from IBAPI """
########## STDLIB IMPORTS ##########
from datetime import datetime, date
from ibapi.execution import ExecutionFilter
########## CUSTOM IMPORTS ##########
from logger import getConsole as console
import config
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

def didAlreadyExecute(client):
    """ Check if Second30 Has Already Executed Today """
    reqId = client.startRequest()
    client.pushRequestData(reqId, {"executed" : False})

    execFilter = ExecutionFilter()
    execFilter.clientId = config.CLIENTID
    execFilter.time = "{} 00:00:00".format(date.today().strftime("%Y%m%d"))

    client.reqExecutions(reqId, execFilter)

    if client.waitForRequest(reqId, purge=True)["executed"]:
        console().info("Already Traded Today!")
        return True
    
    console().info("No Previous Trades Found for Today.")
    return False

########## DATA REQUESTS ##########
