from astral import Location
import sqlite3
from sqlite3 import Error
from datetime import datetime
import configparser


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


config = configparser.ConfigParser()
config.read("../../config.ini")

loc = Location()
loc.latitude = float(config['LOCATION']['Latitude'])
loc.longitude = float(config['LOCATION']['Longitude'])
sun = loc.sun()

database = config['DATABASE']['Path'] + config['DATABASE']['Name']
conn = create_connection(database)
with conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM blinds_schedule")

    rows = cur.fetchall()

    for row in rows:
        task = cur.execute("SELECT * FROM blinds_task WHERE schedule_id = ?",
                           (row[0],)).fetchall()
        if not task:
            time = 0
            if row[3] == 0:
                time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() + row[4]
            elif row[3] == 1:
                time = sun['dawn'].timestamp() + row[4]
            elif row[3] == 2:
                time = sun['sunrise'].timestamp() + row[4]
            elif row[3] == 3:
                time = sun['sunset'].timestamp() + row[4]
            elif row[3] == 4:
                time = sun['dusk'].timestamp() + row[4]

            if time < datetime.now().timestamp():
                time += 86400

            cur.execute("INSERT INTO blinds_task(time, device, action, schedule_id, timeout) VALUES (?, ?, ?, ?, ?)",
                        (int(time), row[1], row[2], row[0], 30))
