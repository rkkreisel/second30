""" Second30 Algo Connection Manager and Thread Handler"""

########## STDLIB IMPORTS ##########
import sys
import signal

########## CUSTOM IMPORTS ##########
import config
from logger import setupLogger, getConsole as console
from ibapi.client import EClient
from wrapper import AppWrapper

########## CLASSES ##########
class AppClient(EClient):
    """ IBAPI App Client """
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

class Second30Trader(AppWrapper, AppClient):
    """ Client, Wrapper, and Logic Bundler """
    def __init__(self):
        AppWrapper.__init__(self)
        AppClient.__init__(self, wrapper=self)
        signal.signal(signal.SIGINT, self.interruptHandler)

    def interruptHandler(self, *_):
        """ Gracefully quit on CTRL+C """
        console().info("Disconnecting From API...")
        self.disconnect()
        sys.exit(0)

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