from datetime import datetime, date, time

from asylum import create_sqlite3_connection

sql_select_meteo = """
SELECT *,
FROM meteo
WHERE time > ?
"""

sql_select_meteo_daily = """
SELECT *
FROM meteo_daily
ORDER BY id DESC
LIMIT 1
"""

sql_insert_daily = """
INSERT INTO meteo_daily (
    day_ordinal,
    temperature_min,
    temperature_avg,
    temperature_max,
    humidity_min,
    humidity_avg,
    humidity_max,
    pressure_min,
    pressure_avg,
    pressure_max,
    dust_PM10_min,
    dust_PM10_avg,
    dust_PM10_max,
    dust_PM25_min,
    dust_PM25_avg,
    dust_PM25_max,
    dust_PM100_min
    dust_PM100_avg,
    dust_PM100_max
    )
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


def main():
    db_con = create_sqlite3_connection()
    last = db_con.execute(sql_select_meteo_daily).fetchone()

    if last is not None:
        start_day = last[1] + 1
        tajm = datetime.combine(date.fromordinal(start_day), time())
        meteo_data = db_con.execute(sql_select_meteo, (tajm.timestamp(), )).fetchall()
    else:
        meteo_data = db_con.execute(sql_select_meteo, (0, )).fetchall()
        start_day = datetime.fromtimestamp(meteo_data[0][1]).date().toordinal()

    print("Zaczynamy od ", str(date.fromordinal(start_day)))

    days = {}
    for x in range(start_day, date.today().toordinal()):
        days[x] = []

    for entry in meteo_data:
        day_number = datetime.fromtimestamp(entry[1]).date().toordinal()
        if day_number in days:
            days[day_number].append(entry)

    for day, datas in sorted(days.items()):

        temperature_min = 1000000
        temperature_avg = 0
        temperature_max = -1000000

        humidity_min = 1000000
        humidity_avg = 0
        humidity_max = -1000000

        pressure_min = 1000000
        pressure_avg = 0
        pressure_max = -1000000

        dust_PM10_min = 1000000
        dust_PM10_avg = 0
        dust_PM10_max = -1000000

        dust_PM25_min = 1000000
        dust_PM25_avg = 0
        dust_PM25_max = -1000000

        dust_PM100_min = 1000000
        dust_PM100_avg = 0
        dust_PM100_max = -1000000


        if len(datas) > 0:
            for entry in datas:
                id, dat, temperature, humidity, pressure, dust_PM10, dust_PM25, dust_PM100 = entry

                temperature_min = min(temperature_min, temperature)
                temperature_avg = temperature_avg + temperature
                temperature_max = max(temperature_max, temperature)

                humidity_min = min(humidity_min, humidity)
                humidity_avg = humidity_avg + humidity
                humidity_max = max(humidity_max, humidity)

                pressure_min = min(pressure_min, pressure)
                pressure_avg = pressure_avg + pressure
                pressure_max = max(pressure_max, pressure)

                dust_PM10_min = min(dust_PM10_min, dust_PM10)
                dust_PM10_avg = dust_PM10_avg + dust_PM10
                dust_PM10_max = max(dust_PM10_max, dust_PM10)

                dust_PM25_min = min(dust_PM25_min, dust_PM25)
                dust_PM25_avg = dust_PM25_avg + dust_PM25
                dust_PM25_max = max(dust_PM25_max, dust_PM25)

                dust_PM100_min = min(dust_PM100_min, dust_PM100)
                dust_PM100_avg = dust_PM100_avg + dust_PM100
                dust_PM100_max = max(dust_PM100_max, dust_PM100)

            temperature_avg /= len(datas)
            humidity_avg /= len(datas)
            pressure_avg /= len(datas)
            dust_PM10_avg /= len(datas)
            dust_PM25_avg /= len(datas)
            dust_PM100_avg /= len(datas)
        else:
            temperature_min = last[2]
            temperature_avg = last[3]
            temperature_max = last[4]

            humidity_min = last[5]
            humidity_avg = last[6]
            humidity_max = last[7]

            pressure_min = last[8]
            pressure_avg = last[9]
            pressure_max = last[10]

            dust_PM10_min = last[11]
            dust_PM10_avg = last[12]
            dust_PM10_max = last[13]

            dust_PM25_min = last[14]
            dust_PM25_avg = last[15]
            dust_PM25_max = last[16]

            dust_PM100_min = last[17]
            dust_PM100_avg = last[18]
            dust_PM100_max = last[19]

        db_con.execute(sql_insert_daily, (
            day,
            temperature_min,
            temperature_avg,
            temperature_max,
            humidity_min,
            humidity_avg,
            humidity_max,
            pressure_min,
            pressure_avg,
            pressure_max,
            dust_PM10_min,
            dust_PM10_avg,
            dust_PM10_max,
            dust_PM25_min,
            dust_PM25_avg,
            dust_PM25_max,
            dust_PM100_min,
            dust_PM100_avg,
            dust_PM100_max
        ))

    db_con.commit()
    db_con.close()


if __name__ == '__main__':
    main()
