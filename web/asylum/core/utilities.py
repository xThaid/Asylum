import datetime


def unixtime_to_strftime(time, format_str):
    return [datetime.datetime.fromtimestamp(o).strftime(format_str) for o in time]
