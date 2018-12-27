import datetime

from astral import Location

from asylum import config
from asylum import create_sqlite3_connection


SCHEDULE_TASK_TIMEOUT = 60 * 30

loc = Location()
loc.latitude = float(config['LOCATION']['Latitude'])
loc.longitude = float(config['LOCATION']['Longitude'])


def calcHours(day):
    hours = {}

    sun = loc.sun(date=day)
    hours[1] = sun['dawn']
    hours[2] = sun['sunrise']
    hours[3] = sun['noon']
    hours[4] = sun['sunset']
    hours[5] = sun['dusk']
    hours[6] = datetime.datetime.combine(day, datetime.time())
    return hours


today = datetime.date.today()
todayHours = calcHours(today)
tommorowHours = calcHours(today + datetime.timedelta(days=1))

conn = create_sqlite3_connection()
try:
    cur = conn.cursor()
    cur.execute("SELECT id, device, action, hour_type, time_offset FROM blinds_schedule")

    schedules = cur.fetchall()

    for sched in schedules:
        sched_id, device_id, action_id, hour_type, time_offset = sched

        task = cur.execute("SELECT * FROM blinds_task WHERE schedule_id = ?",
                           (sched_id,)).fetchall()
        if not task:
            offset = datetime.timedelta(minutes=time_offset)
            time = todayHours[hour_type] + offset

            if time.timestamp() < datetime.datetime.now().timestamp():
                time = tommorowHours[hour_type] + offset

            cur.execute("INSERT INTO blinds_task (time, device, action, schedule_id, timeout) \
                VALUES (?, ?, ?, ?, ?)", (
                int(time.timestamp()),
                device_id,
                action_id,
                sched_id,
                SCHEDULE_TASK_TIMEOUT))
finally:
    conn.commit()
    conn.close()
