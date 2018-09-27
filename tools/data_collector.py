from sqlite3 import Error
import requests
import re
import sys

import config
import db

ENERGY_IMPORT_OFFSET = 471851
ENERGY_EXPORT_OFFSET = 1124061


def collect_flara(url):
    try:
        res = requests.get(url + "list_en.html").text
        if res != "<tr class='msgfail'><td>Devices not found.</td></tr>":
            res = requests.get(url + "FF00000080087B2E00010102000001EF/data_en.html").text
            energy = re.search("(?<=Total energy</div><div class='pvalue vok'>)[0-9.]*", res)
            return float(energy.group())
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(e)
        return None


def collect_emeter(url):
    try:
        return requests.get(url).json()
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def main():
    cfg = config.config

    energy_production = collect_flara(cfg['SUBSYSTEMS']['flara_url'])
    emeter_reading = collect_emeter(cfg['SUBSYSTEMS']['emeter_url'])
    if energy_production is None or emeter_reading is None:
        print("Cannot collect data. Quiting...")
        sys.exit(1)

    energy_production = int(energy_production * 1000)
    energy_import = int(float(emeter_reading['37']) * 1000) \
        + ENERGY_IMPORT_OFFSET
    energy_export = int(float(emeter_reading['38']) * 1000) \
        + ENERGY_EXPORT_OFFSET

    db_conn = db.create_connection()

    try:
        cursor = db_conn.cursor()
        sql = "INSERT INTO energy (production, import, export) \
            VALUES (?, ?, ?)"
        cursor.execute(sql, (energy_production, energy_import, energy_export))
        db_conn.commit()
        cursor.close()
    except Error as e:
        print(e)
    finally:
        db_conn.close()


if __name__ == '__main__':
    main()
