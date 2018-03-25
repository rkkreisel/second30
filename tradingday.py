""" Trading Day and Market Hours Tracking """
########## STDLIB IMPORTS ##########
import re
from datetime import datetime, date, timedelta

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
        self.marketOpen = False
        self.normalDay = self.isNormalTradingDay()
        self.thirtyAfterOpen = False
        self.logDayDetails()

    def __eq__(self, other):
        return self.today == other.today

    def isNormalTradingDay(self):
        """ Check if Date has Normal Trading Hours. Needs config var"""

        def ignoreDate():
            """ Ignore Bad Days of Malformed Date Strings """
            ignore = input("Continue Anyway? (y/n) > ")
            return True if ignore.lower() == 'y' else False

        try:
            days = self.contractDetails.tradingHours.split(";")
            today = [x for x in days if x.split(":")[0] == self.today.strftime("%Y%m%d")]

            if not today:
                console().error("Missing Contract Market Hours for Today.")
                return ignoreDate()

            hours = today[0].split(":")[1]

            # Trading Hours Cross Mutliple Dates
            if hours != "CLOSED" and len(hours.split('-')[1]) == 8:
                hours = parseMultiDayHours(self.contractDetails.tradingHours)

            console().info("Today's Trading Hours Are: {}".format(hours))

            if hours == "CLOSED" or hours != config.NORMAL_TRADING_HOURS:
                return ignoreDate()
            return True

        except (IndexError, AttributeError):
            console().warning("Unable to Calculate Trading Hours.")
            return ignoreDate()

    def isMarketOpen(self):
        """ Check if the Market Is Currently Open """
        if not self.normalDay:
            return False
        now = datetime.now()
        if now.hour >= 9 and now.hour < 16:
            if now.hour == 9 and now.minute < 30:
                return False
            return True
        return False

    def logDayDetails(self):
        """ Write Information about the Current Trading Day to the Console/Log """
        console().info("Today is {}.".format(self.today.strftime(DATE_FMT)))
        if self.normalDay:
            console().info("Today is a Valid Day for Trading")
        else:
            console().info("Today is not a Valid Trading Day. Sleeping Until Tomorrow")

    def is30AfterOpen(self):
        """ Check if it is 30 minutes after market open at 9:30AM """
        if self.thirtyAfterOpen: return True
        now = datetime.now()
        if now.hour >= 10 and now.microsecond > 0 and self.normalDay:
            console().info("It is 30 minutes after Market Opening.")
            self.thirtyAfterOpen = True
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

def parseMultiDayHours(tradingHours):
    """ Parse TradingHours when Mutli-Date Format is Returned """
    multi_re = re.compile(r"([0-9]{8}):([0-9]+)-([0-9]{8}):([0-9]+)")
    days = tradingHours.split(";")
    today = datetime.today().strftime("%Y%m%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
    hours = []

    for day in days:
        match = multi_re.match(day)
        if not match:
            continue

        if match.group(1) not in [today, yesterday]:
            continue

        if match.group(3) not in [today, yesterday]:
            continue

        hours += ["{0}-{1}".format(match.group(2), match.group(4))]

    return ",".join(hours)
