"""
    Second30 Algorithm Logic
"""
import logging
from sys import exit as sysexit
from ib_insync import IB
from ib_insync.contract import ContFuture

import config
import helpers


class Algo():
    """ Second30 Algorithm Class """
    def __init__(self, ib: IB):
        self.ib = ib

    def run(self):
        """ Execute the Algorithm """
        contract = self.get_contract()
        open_today = helpers.is_open_today(contract)
        if not open_today:
            logging.error("Today is not a Valid Trading Day")
            sysexit()
        logging.info("Market is Open Today")


    def get_contract(self):
        """ Get the Current Futures Symbol Details """
        contract = self.ib.reqContractDetails(
            ContFuture(symbol=config.SYMBOL, exchange=config.EXCHANGE)
        )
        if not contract:
            logging.error("Failed to Grab Continuous Future {}".format(config.SYMBOL))
            sysexit()
        else:
            return contract[0]
