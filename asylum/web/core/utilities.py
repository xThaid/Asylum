import datetime
import time


def unixtime_to_strftime(unixtime, format_str):
    if type(unixtime) == list:
        return [datetime.datetime.fromtimestamp(o).strftime(format_str) for o in unixtime]
    else:
        return datetime.datetime.fromtimestamp(unixtime).strftime(format_str)


def strftime_to_unixtime(strftime, format_str):
    if type(strftime) == list:
        return [time.mktime(datetime.datetime.strptime(o, format_str).timetuple()) for o in strftime]
    else:
        return time.mktime(datetime.datetime.strptime(strftime, format_str).timetuple())

def average_in(l):
    list_not_none = list(filter(lambda x: x is not None, l))
    if len(list_not_none) == 0:
        return None
    return sum(list_not_none)/len(list_not_none)

def round_in(number, position):
    if number is None:
        return None
    return round(number, position)

def max_in(l):
    list_not_none = list(filter(lambda x: x is not None, l))
    if len(list_not_none) == 0:
        return None
    return max(list_not_none)
