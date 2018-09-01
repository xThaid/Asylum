import sqlite3
import sys
import os
from sqlite3 import Error


def create_connection(db_file, db_script):
    try:
        conn = sqlite3.connect(db_file)
        try:
            f = open(db_script)
            conn.executescript(f.read())
            f.close()
        except IOError as e:
            print(e)
            sys.exit(2)
        conn.commit()
        conn.close()
        print("Database created successfully")
    except Error as e:
        print(e)


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.realpath(__file__)) + '\\'
    create_connection(current_dir + 'asylum.sqlite', current_dir + 'schema.sql')
