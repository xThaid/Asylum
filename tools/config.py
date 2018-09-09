import configparser

CONFIG_LOCATION = "/home/thaid/Dev/repos/Asylum/config.ini"


def loadConfig():
    config = configparser.ConfigParser()
    config.read(CONFIG_LOCATION)
    return config
