import sqlite3
import configparser
import os


def create_connection():
    config = configparser.ConfigParser()
    config.read(os.environ['ASYLUM_CONFIG'])
    db_file = config['DATABASE']['Path']
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None
