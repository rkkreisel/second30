""" Track Requests to IBAPI. Hold Output. Monitor Completion """

########## CUSTOM IMPORTS ##########
from logger import getConsole as console

########## CLASS DEFINITION ##########
class RequestManager():
    """ Manage Request ID's and their Results """

    REQUEST_ID = "REQUEST_ID_PLACEHOLDER"

    def __init__(self):
        self.nextRequestId = 100
        self.data = {}
        console().info("Initialized The Request Manager")

    def startRequest(self):
        """ Generate a new Request ID """
        requestId = self.nextRequestId
        while requestId in self.data.keys():
            self.nextRequestId += 1
            requestId += 1
        if self.nextRequestId == 1000:
            self.nextRequestId = 100
        else:
            self.nextRequestId += 1
        self.data[requestId] = {"complete" : False}
        return requestId

    def pushRequestData(self, reqId, data):
        """ Add new Response Data for an ID """
        if not isinstance(data, dict):
            print("Error. Non Dict Data Push")
            return
        self.data[reqId].update(data)

    def getRequestData(self, reqId):
        """ Retreive Response Data from and ID """
        if not self.data[reqId]["complete"]:
            return None
        self.data[reqId].pop("complete", None)
        return self.data[reqId]

    def finishRequest(self, reqId):
        """ Signal that a Request has Completed """
        self.data[reqId]["complete"] = True

    def purgeRequest(self, reqId):
        """ Remove A Request """
        self.data.pop(reqId, False)

    def waitForRequest(self, reqId, purge=False):
        """ Pause Execution Until a Request Retunrns """
        while self.data[reqId] is None:
            pass
        while not self.data[reqId]["complete"]:
            pass
        data = self.getRequestData(reqId)
        if purge:
            self.purgeRequest(reqId)
        return data

    def subscribe(self, name, startFunc, startArgs, stopFunc, stopArgs):
        """ Create Subscription To IBAPI """
        requestId = self.startRequest()
        startArgs = [requestId if x == self.REQUEST_ID else x for x in startArgs]
        stopArgs = [requestId if x == self.REQUEST_ID else x for x in stopArgs]

        self.pushRequestData(requestId, {"subscription": (name, stopFunc, stopArgs)})
        startFunc(*startArgs)
        return requestId

    def stopSubscription(self, reqId):
        """ Stop a Single Subscription and notify IBAPI """
        try:
            name, stopFunc, stopArgs = self.data[reqId]["subscription"]
            console().info("Stopping Subscription: {}".format(name))
        except KeyError:
            console().error("Failed to Stop Subscription: {}.".format(name))
            console().error(self.data)
            return
        self.data.pop(reqId, None)
        stopFunc(*stopArgs)

    def stopAllSubscriptions(self):
        """ Stop all Current Subscriptions and notify IBAPI """
        console().info("Stopping All Active Subscriptions...")
        subs = [x for x, keys in self.data.items() if "subscription" in keys]
        for sub in subs:
            self.stopSubscription(sub)

    def printStatus(self):
        """ Show Current Subscriptions and Price Data """

        print("\nSubscriptions: ")
        subs = {k: v for k, v in self.data.items() if "subscription" in v.keys()}
        if not subs: print("\tNone")
        else:
            for key, value in subs.items():
                print("\tID: {}. Name: {}".format(key, value["subscription"][0]))

        print("Streaming Data:")
        streams = {k: v for k, v in self.data.items() if "price" in v.keys()}
        if not streams: print("\tNone")
        else:
            for key, value in streams.items():
                print("\t{}: {}".format(value["subscription"][0], value["price"]))

        print("Positions:")
        positions = self.logic.account.positions #pylint: disable=no-member
        if not positions: print("\tNone")
        else:
            for key, value in positions.items():
                print("\t{}: #Contracts: {}".format(key, value[1]))

        print("Orders:")
        orders = self.logic.account.openOrders #pylint: disable=no-member
        if not orders: print("\tNone")
        else:
            for key, value in orders.items():
                print("\tID {}: Contract: {}. Order: {}. State: {}".format(
                    key, value[0].localSymbol, value[1], value[2]))
