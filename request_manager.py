""" Track Requests to IBAPI. Hold Output. Monitor Completion """

########## CUSTOM IMPORTS ##########
from logger import getConsole as console

########## CLASS DEFINITION ##########
class RequestManager():
    """ Manage Request ID's and their Results """
    def __init__(self):
        self.nextRequestId = 100
        self.data = {}
        console().info("Initialized The Request Manager")

    def startRequest(self):
        """ Generate a new Request ID """
        requestId = self.nextRequestId
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
        self.data[reqId].pop("complete")
        return self.data[reqId]

    def finishRequest(self, reqId):
        """ Signal that a Request has Completed """
        self.data[reqId]["complete"] = True

    def waitForRequest(self, reqId):
        """ Pause Execution Until a Request Retunrns """
        while self.data[reqId] is None:
            pass
        while not self.data[reqId]["complete"]:
            pass
        return self.getRequestData(reqId)
