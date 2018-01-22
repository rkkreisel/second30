""" Algorithm Requests for Data from IBAPI """
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

########## DATA REQUESTS ##########
