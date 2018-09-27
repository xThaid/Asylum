from astral import Location
from datetime import datetime

import config
import db

cfg = config.config

loc = Location()
loc.latitude = float(cfg['LOCATION']['Latitude'])
loc.longitude = float(cfg['LOCATION']['Longitude'])
sun = loc.sun()

conn = db.create_connection()
try:
    cur = conn.cursor()
    cur.execute("SELECT * FROM blinds_schedule")

    rows = cur.fetchall()

    for row in rows:
        task = cur.execute("SELECT * FROM blinds_task WHERE schedule_id = ?",
                           (row[0],)).fetchall()
        if not task:
            time = 0
            now = datetime.now()
            if row[3] == 0:
                time = now.replace(hour=0, minute=0, second=0, microsecond=0) \
                    .timestamp() + row[4]
            elif row[3] == 1:
                time = sun['dawn'].timestamp() + row[4]
            elif row[3] == 2:
                time = sun['sunrise'].timestamp() + row[4]
            elif row[3] == 3:
                time = sun['sunset'].timestamp() + row[4]
            elif row[3] == 4:
                time = sun['dusk'].timestamp() + row[4]

            if time < now.timestamp():
                time += 86400

            cur.execute("INSERT INTO blinds_task (time, device, action, schedule_id, timeout) \
                VALUES (?, ?, ?, ?, ?)", (int(time), row[1], row[2], row[0], 30 * 60))
finally:
    conn.commit()
    conn.close()
