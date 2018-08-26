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
