import datetime
import re
import logging

class TradingDay():
    def __init__(self, liquidHours, skew=0):
        self.open_time = None
        self.close_time = None
        self.openToday = None
        self.today = datetime.date.today()
        self.todayString = self.today.strftime("%B %d, %Y")
        self.skew = skew
        self.high = None
        self.low = None
        
        self.get_market_hours(liquidHours)
    
    def get_market_hours(self, liquidHours):
        market_hours = liquidHours.split(";")[0].split(":")[1]
        
        if market_hours == "CLOSED":
            self.openToday = False
            self.open_time = "CLOSED"
            self.close_time = "CLOSED"
            return

        print("trading day info: {}".format(market_hours))
        #open_time, close_time = market_hours.split("-")
        open_time = "0930"
        close_time = "1600"
        today = datetime.datetime.today()
        self.open_time = datetime.datetime(year=today.year, month=today.month,
            day=today.day, hour=int(open_time[0:2]),
            minute=int(open_time[2:4]))
        self.close_time = datetime.datetime(year=today.year, month=today.month,
            day=today.day, hour=int(close_time[0:2]),
            minute=int(close_time[2:4]))
        self.openToday = True
    
    def get_now(self):
            local = datetime.datetime.today()
            seconds = local.second - self.skew
            delta = datetime.timedelta(seconds=seconds)
            now = local - delta  
                
            return now 
            
    def is_market_open(self):
        if not self.openToday:
            return False
        
        now = self.get_now()
        
        if now >= self.open_time and now < self.close_time:
            return True
        return False
        
    def is_30_after_open(self):
        delta = datetime.timedelta(minutes=30)
        now = self.get_now()

        if now >= (self.open_time + delta):
            return True
        return False
            
    def is_10_before_close(self):
        delta = datetime.timedelta(minutes=10)
        now = self.get_now()
        
        if now >= (self.close_time - delta):
            return True
        return False
        
    def is_highlow_set(self):
        if self.high and self.low:
            return True
        return False
        
    def prompt_highlow(self):
        self.high = None
        self.low = None
        price_re = re.compile("^-?\d+.?\d*$")
        
        def prompt_price(price_type):
            print("Please Enter the {} for the Day: ".format(price_type))
            price = input("> $")
            print("You entered ${}".format(price))
            if not price_re.match(price):
                print("Error. Invalid Price Value") 
                return None
            print("\nProceed with value: ${}? (y/n)".format(price))
            confirm = input("> ")
            if confirm == "Y" or confirm == "y":
                return float(price)
            return None
        
        while self.high is None:        
            self.high = prompt_price("High")
        while self.low is None:
            self.low = prompt_price("Low")