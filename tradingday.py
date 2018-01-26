""" Trading Day and Market Hours Tracking """
########## STDLIB IMPORTS ##########
from datetime import datetime, date

########## CUSTOM IMPORTS ##########
import config
from logger import getConsole as console

########## CONSTANTS ##########
DATE_FMT = "%B %d, %Y"

########## CLASS DEFINITION ##########
class TradingDay():
    """ Validates the Current Date and time for Trading Eligibility"""
    def __init__(self, contractDetails):
        self.today = date.today()
        self.contractDetails = contractDetails
        self.executedToday = False
        self.marketOpen = False
        self.normalDay = self.isNormalTradingDay()
        self.thirtyAfterOpen = False
        self.tenBeforeClose = False
        self.logDayDetails()

    def isNormalTradingDay(self):
        """ Check if Date has Normal Trading Hours. Needs config var"""
        days = self.contractDetails.tradingHours.split(";")
        dateString = self.today.strftime("%Y%m%d")
        today = [x for x in days if x.split(":")[0] == dateString]
        if not today:
            console().error("Missing Contract Market Hours for Today.")
        hours = today[0].split(":")[1]
        if hours == "CLOSED" or hours != config.NORMAL_TRADING_HOURS:
            return False
        return True

    def isMarketOpen(self):
        """ Check if the Market Is Currently Open """
        if not self.normalDay:
            return False
        now = datetime.now()
        if now.hour >= 9 and now.hour < 16:
            if now.hour == 9 and now.minutes < 30:
                return False
            return True
        return False

    def logDayDetails(self):
        """ Write Information about the Current Trading Day to the Console/Log """
        console().info("Today is {}.".format(self.today.strftime(DATE_FMT)))
        hours = self.contractDetails.tradingHours.split(";")[0].split(":")[1]
        console().info("Today's Trading Hours Are: {}".format(hours))
        if self.normalDay:
            console().info("Today is a Valid Day for Trading")
        else:
            console().info("Today is not a Valid Trading Day. Sleeping Until Tomorrow")

    def is30AfterOpen(self):
        """ Check if it is 30 minutes after market open at 9:30AM """
        if self.thirtyAfterOpen: return True
        now = datetime.now()
        if now.hour >= 9 and now.minute >= 30:
            console().info("It is 30 minutes after Market Opening.")
            self.thirtyAfterOpen = True
            return True
        return False

    def is10BeforeClose(self):
        """ Check if it is 10 minutes before market close at 4:00PM """
        if self.tenBeforeClose: return True
        now = datetime.now()
        if now.hour == 15 and now.minute >= 50:
            console().info("It is less than 10 minutes before Market Close.")
            self.tenBeforeClose = True
            return True
        return False

########## Functions ##########
def updateToday(tradingDay):
    """ Keep Date and Market Status Current """
    if  date.today() != tradingDay.today:
        tradingDay = TradingDay(tradingDay.contractDetails)

    if tradingDay.isMarketOpen():
        if not tradingDay.marketOpen:
            tradingDay.marketOpen = True
            console().info("The Market Has Opened")
    else:
        if tradingDay.marketOpen:
            tradingDay.marketOpen = False
            console().info("The Market Has Closed")
    return tradingDay
