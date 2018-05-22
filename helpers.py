"""
    Second30 Helper Functions
"""
import xml.etree.ElementTree as ET
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

def parseAdvisorConfig(xml):
    """ Get # Of Contracts from Current Advisor Profile """
    root = ET.fromstring(xml)
    profileTag = None
    for profile in  root.getchildren():
        for attrib in profile.getchildren():
            if attrib.tag == 'name':
                if attrib.text.lower() == config.ALLOCATION_PROFILE.lower():
                   profileTag = profile
    if not profileTag: return None

    allocations = None
    for attrib in profileTag.getchildren():
        if attrib.tag == "ListOfAllocations":
            allocations = attrib
    if not allocations: return None 
    
    amount = 0
    for allocation in allocations.getchildren():
        for attrib in allocation:
             if attrib.tag == "amount":
                 amount += int(float(attrib.text))
    return amount
