""" Trading Day and Market Hours Tracking """
########## STDLIB IMPORTS ##########
from datetime import datetime

########## CUSTOM IMPORTS ##########
import config
from logger import getConsole as console

########## CONSTANTS ##########
DATE_FMT = "%B %d, %Y"

########## CLASS DEFINITION ##########

class TradingDay():
    """ Validates the Current Date and time for Trading Eligibility"""
    def __init__(self, contractDetails):
        self.today = datetime.today()
        self.contractDetails = contractDetails
        self.executedToday = False
        console().info("Today is {}.".format(self.today.strftime(DATE_FMT)))
        if self.isNormalTradingDay():
            console().info("Today is a Valid Day for Trading")
        else:
            console().info("Today is not a Valid Trading Day. Sleeping Until Tomorrow")

    def isNormalTradingDay(self):
        """ Check if Date has Normal Trading Hours. Needs config var"""
        today = self.contractDetails.tradingHours.split(";")[0]
        date, hours = today.split(":")

        if date != self.today.strftime("%Y%m%d"):
            console().error("Trading Hours Date Mismatch!")

        if hours == "CLOSED" or hours != config.NORMAL_TRADING_HOURS:
            return False
        return True

    def isMarketOpen(self):
        """ Check if the Market Is Currently Open """
        if not self.isNormalTradingDay():
            return False
        now = datetime.now()
        if now.hour >= 9 and now.hour < 16:
            if now.hour == 9 and now.minutes < 30:
                return False
            return True
        return False
