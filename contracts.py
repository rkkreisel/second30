""" Futures Contract Generation / Selection """
########## STDLIB IMPORTS ##########
from datetime import datetime, date, timedelta

########## CUSTOM IMPORTS ##########
from ibapi.contract import Contract

import config
from logger import getConsole as console

########## FUNCTIONS ##########

def getContractDetails(client):
    """ Request Contract Details for Base Contract"""
    baseContract = getBaseContract()
    reqId = client.startRequest()

    client.reqContractDetails(reqId, baseContract)
    console().info("Requesting Details For: {}".format(baseContract.symbol))

def getCurrentFuturesContract(contractDetails):
    """ Select the Most Current Symbol """
    soonest = None
    for _, data in contractDetails.items():
        expireString = data.summary.lastTradeDateOrContractMonth
        expireYear = int(expireString[:4])
        expireMonth = int(expireString[4:6])
        expireDay = int(expireString[6:8])

        expireDate = datetime(year=expireYear, month=expireMonth, day=expireDay)

        if expireDate <= datetime.today():
            continue

        if soonest is None or (expireDate < soonest[0]): # pylint: disable=unsubscriptable-object
            soonest = [expireDate, data]

    contract = soonest[1]
    console().info("Picked Current FUT Contract: {}".format(contract.summary.localSymbol))
    return contract

def updateFuture(client, future):
    """ Get New Futures Contracts Every Day"""
    contractDate = future.tradingHours.split(";")[0].split(":")[0]
    currentDates = [x.strftime("%Y%m%d") for x in [date.today(), date.today() - timedelta(days=1)]]
    if contractDate not in currentDates:
        getContractDetails(client)

def getBaseContract():
    """ Generic Base Contract Generator"""
    contract = Contract()
    contract.symbol = config.SYMBOL
    contract.secType = "FUT"
    contract.exchange = config.EXCHANGE
    return contract
