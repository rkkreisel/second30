"""
    Second30 Helper Functions
"""
from datetime import datetime, timedelta
from re import compile as compile_re
from ib_insync.contract import Contract

import config

def is_open_today(contract: Contract):
    """ Parse contract Trading Hours to Check if Valid Trading Day"""
    date_re = compile_re(r"([0-9]{8}):([0-9]+)-([0-9]{8}):([0-9]+)")
    days = contract.tradingHours.split(";")
    today = datetime.today().strftime("%Y%m%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
    hours = []

    for day in days:
        match = date_re.match(day)
        if not match: continue
        if match.group(1) not in [today, yesterday]: continue
        if match.group(3) not in [today, yesterday]: continue
        hours += ["{0}-{1}".format(match.group(2), match.group(4))]

    today_hours = ",".join(hours)
    if today_hours == config.NORMAL_TRADING_HOURS:
        return True
    return False
