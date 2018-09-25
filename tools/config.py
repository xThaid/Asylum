import configparser

CONFIG_LOCATION = "../config.ini"


def loadConfig():
    config = configparser.ConfigParser()
    config.read(CONFIG_LOCATION)
    return config
