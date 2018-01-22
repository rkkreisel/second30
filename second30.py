""" Second30 Algo Connection Manager and Thread Handler"""

########## STDLIB IMPORTS ##########
import sys
import signal

########## CUSTOM IMPORTS ##########
import config

from ibapi.client import EClient

from logger import setupLogger, getConsole as console
from wrapper import AppWrapper
from request_manager import RequestManager

########## CLASSES ##########
class AppClient(EClient):
    """ IBAPI App Client """
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

class Second30Trader(AppWrapper, AppClient, RequestManager):
    """ Client, Wrapper, and Logic Bundler """
    def __init__(self):
        AppWrapper.__init__(self)
        AppClient.__init__(self, wrapper=self)
        RequestManager.__init__(self)
        signal.signal(signal.SIGINT, self.interruptHandler)
        signal.signal(signal.SIGTSTP, self.statusHandler)

    def interruptHandler(self, *_):
        """ Gracefully quit on CTRL+C """
        console().info("Disconnecting From API...")
        self.stopAllSubscriptions()
        self.disconnect()
        sys.exit(0)

    def statusHandler(self, *_):
        """ Show Price and Other Data on Ctrl + Z """
        self.printStatus()

########## MAIN ##########
def main():
    """ Setup Logging and Intialize Algo Trader """

    setupLogger()
    console().info("Started Second30 Trader v{}".format(config.VERSION))

    app = Second30Trader()

    try:
        console().info("Connecting to TWS API at {}:{}. Client ID: {}"
                       .format(config.HOST, config.PORT, config.CLIENTID))

        app.connect(config.HOST, config.PORT, clientId=config.CLIENTID)

        if app.isConnected():
            console().info("Connection Successful.  Server Version: {}".format(app.serverVersion()))
            app.run()
        else:
            console().info("Connection Failed")
    except:
        raise

if __name__ == "__main__":
    main()
