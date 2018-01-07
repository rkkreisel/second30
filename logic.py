""" Trading Algorithm Definition """

########## STDLIB IMPORTS ##########
import threading

########## CUSTOM IMPORTS ##########
from logger import log

########## CLASS DEFINITON ##########
class AppLogic(threading.Thread):
    """ Thread to Hold Algorithm Logic """
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.daemon = True
        self.app = app
        self.name = "AppLogic"

    def run(self):
        pass
