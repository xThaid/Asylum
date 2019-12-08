import configparser
import sqlite3

CONFIG_LOCATION = "/home/thaid/Dev/repos/Asylum/config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_LOCATION)


def create_sqlite3_connection():
    db_file = config['DATABASE']['Path']
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None
