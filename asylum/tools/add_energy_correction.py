import sys
import datetime

from sqlite3 import Error

from asylum import create_sqlite3_connection

def main():
    db_conn = create_sqlite3_connection()
    cursor = db_conn.cursor()

    if len(sys.argv) != 3:
        print("Usage: [date in format {}] [correction]".format(datetime.date.today().isoformat()))
        return

    date = sys.argv[1];
    val = int(float(sys.argv[2]) * 1000)

    try:
        sql = "INSERT INTO energy_corrections (date, correction) \
            VALUES (?, ?)"
        cursor.execute(sql, (date, val))
        db_conn.commit()
    except Error as e:
        print(e)

    cursor.close()
    db_conn.close()

if __name__ == '__main__':
    main()
