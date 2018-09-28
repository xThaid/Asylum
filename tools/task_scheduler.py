import datetime
import config
import db

from astral import Location

SCHEDULE_TASK_TIMEOUT = 60 * 30

cfg = config.config

loc = Location()
loc.latitude = float(cfg['LOCATION']['Latitude'])
loc.longitude = float(cfg['LOCATION']['Longitude'])


def calcHours(day):
    hours = {}

    sun = loc.sun(date=day)
    hours[1] = sun['dawn']
    hours[2] = sun['sunrise']
    hours[3] = sun['noon']
    hours[4] = sun['sunset']
    hours[5] = sun['dusk']
    hours[6] = datetime.datetime.combine(day, datetime.datetime.min.time())
    return hours


today = datetime.date.today()
todayHours = calcHours(today)
tommorowHours = calcHours(today + datetime.timedelta(days=1))

conn = db.create_connection()
try:
    cur = conn.cursor()
    cur.execute("SELECT * FROM blinds_schedule")

    schedules = cur.fetchall()

    for sched in schedules:
        sched_id, device_id, action_id, hour_type, time_offset = sched

        task = cur.execute("SELECT * FROM blinds_task WHERE schedule_id = ?",
                           (sched_id)).fetchall()
        if not task:
            offset = datetime.timedelta(seconds=time_offset)
            time = todayHours[hour_type] + offset

            if time < datetime.datetime.now():
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
