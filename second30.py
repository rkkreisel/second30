"""
    Second30
"""
import logging
from sys import exit as sys_exit
from ib_insync import IB

import config
import logger
from logic import Algo

def main(ib: IB):
    """ Connect to IB and Kick off Algo """
    try:
        ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID)
        ib.reqMarketDataType(config.DATATYPE)
    except OSError:
        logging.error("Connection Failed.")
        sys_exit()
    algo = Algo(ib)
    algo.run()

if __name__ == '__main__':
    logger.setup()
    main(IB())
