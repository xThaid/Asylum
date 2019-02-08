from sqlite3 import Error

from asylum import create_sqlite3_connection
from asylum.meteo import meteo_data


def main():
    db_conn = create_sqlite3_connection()
    cursor = db_conn.cursor()
    data = meteo_data.get_data()

    if data is not None and data['is_data_correct']:
        try:
            sql = "INSERT INTO meteo (temperature, humidity, pressure, dust_PM10, dust_PM25, dust_PM100) \
                VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (
                data['temperature'],
                data['humidity'],
                data['pressure'],
                data['dust_PM10'],
                data['dust_PM25'],
                data['dust_PM100']
            ))
            db_conn.commit()
        except Error as e:
            print(e)

        cursor.close()
        db_conn.close()


if __name__ == '__main__':
    main()
