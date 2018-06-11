"""
    Second30
"""
import logger
from sys import exit as sys_exit
from ib_insync import IB

import config
import logger
from logic import Algo
from events import registerEvents

def main(ib: IB):
    """ Connect to IB and Kick off Algo """
    try:
        registerEvents(ib)
        logger.getLogger().info("Connecting...")
        ib.connect(config.HOST, config.PORT, clientId=config.CLIENTID)
        ib.reqMarketDataType(config.DATATYPE)
    except OSError:
        logger.getLogger().error("Connection Failed.")
        sys_exit()
    algo = Algo(ib)
    algo.run()

if __name__ == '__main__':
    logger.setup()
    main(IB())
