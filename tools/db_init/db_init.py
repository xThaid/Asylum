import sqlite3
import sys
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
    create_connection('asylum.sqlite', 'schema.sql')
