import sqlite3
from sqlite3 import Error
import requests
import re


def insert_to_db(table, power, energy):
    try:
        connection = sqlite3.connect('/home/primpi/Asylum/Databases/asylum.sqlite')

        try:
            with connection:
                cursor = connection.cursor()
                sql = "INSERT INTO " + table + " ( power, energy) VALUES (?, ?)"
                cursor.execute(sql, (power, energy))
                connection.commit()
                cursor.close()
        finally:
            connection.close()

    except Error as e:
        print(e)


def collect_consumption():
    try:
        res = requests.get('http://192.168.1.102').json()
        insert_to_db("Consumption", int(res["power"]), int(res["energy"]))
    except requests.exceptions.RequestException:
        pass


def collect_production():
    address = "http://192.168.1.35/"
    try:
        res = requests.get(address + "list_en.html").text
        if res != "<tr class='msgfail'><td>Devices not found.</td></tr>":
            res = requests.get(address + "FF00000080087B2E00010102000001EF/data_en.html").text
            power = re.search("(?<=Active power</div><div class='pvalue vok'>)[0-9.]*", res)
            energy = re.search("(?<=Total energy</div><div class='pvalue vok'>)[0-9.]*", res)

            insert_to_db('Production', int(power.group()), float(energy.group()) * 1000)

    except requests.exceptions.RequestException:
        pass


if __name__ == '__main__':
    collect_consumption()
    collect_production()
