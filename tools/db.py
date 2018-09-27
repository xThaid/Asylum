import sqlite3

import config


def create_connection():
    cfg = config.config
    db_file = cfg['DATABASE']['Path']
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None
