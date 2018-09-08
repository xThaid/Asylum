import sys
import os

import db


if __name__ == '__main__':
    try:
        current_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
        schema_loc = current_dir + 'db_schema.sql'
        schema = open(schema_loc).read()
    except IOError as e:
        print(e)
        sys.exit(2)

    conn = db.create_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()
