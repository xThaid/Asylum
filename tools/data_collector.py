import db
import energy_data
from sqlite3 import Error


def main():

    db_conn = db.create_connection()
    data = energy_data.get_data()

    try:
        cursor = db_conn.cursor()
        sql = "INSERT INTO energy (production, import, export, power_production, power_import, power_export) \
            VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (
            data['total_energy_production'],
            data['total_energy_import'],
            data['total_energy_export'],
            data['power_production'],
            data['power_import'],
            data['power_export']
        ))
        db_conn.commit()
        cursor.close()
    except Error as e:
        print(e)
    finally:
        db_conn.close()


if __name__ == '__main__':
    main()
