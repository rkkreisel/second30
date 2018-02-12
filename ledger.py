""" Write Trade Ledger to CSV File """
########## STDLIB IMPORTS ##########
from csv import writer, QUOTE_MINIMAL
from os import stat
from datetime import datetime
########## CUSTOM IMPORTS ##########
import config

########## CLASS ##########
class Ledger():
    """ Ledger Class to Record Order Status in CSV """
    def __init__(self):
        self.f = open(config.LEDGERFILE, 'a')
        self.writer = writer(self.f, quoting=QUOTE_MINIMAL)
        if stat(config.LEDGERFILE).st_size == 0:
            self.writeHeaders()

    def close(self):
        """ Close the underlying CSV File """
        self.f.close()

    def writeHeaders(self):
        """ Add headers to a new CSV """
        headers = ["DATE", "TIME", "ORDER_ID", "SYMBOL", "ACTION", "ORDER_TYPE",
                   "QUANTITY", "PRICE", "STATUS", "VERSION"]
        self.writer.writerow(headers)

    def log(self, orderId, symbol, action, orderType, quantity, price, status):
        """ Write a new Order Status Row to the CSV """
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        version = "Second30 v{}".format(config.VERSION)
        self.writer.writerow(
            [date, time, orderId, symbol, action, orderType, quantity, price, status, version]
        )
        self.f.flush()
        