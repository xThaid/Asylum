import db
from datetime import datetime, date, timedelta, time


def main():
    db_con = db.create_connection()
    last = db_con.execute("SELECT day_ordinal, production, import, export from energy_daily order by id desc limit 1").fetchone()

    sql = "SELECT id, time, production, import, export, power_production, power_import, power_export from energy where time > ?"
    production = import_ = export = 0
    if last is not None:
        start_date = date.fromordinal(last[0]) + timedelta(days=1)
        tajm = datetime.combine(start_date, time())
        energy_data = db_con.execute(sql, (tajm.timestamp(), )).fetchall()
        production = last[1]
        import_ = last[2]
        export = last[3]
    else:
        energy_data = db_con.execute(sql, (0, )).fetchall()
        start_date = datetime.fromtimestamp(energy_data[0][1]).date()

    max_power_production = 0
    max_power_import = 0
    max_power_export = 0
    max_power_consumption = 0
    max_power_use = 0
    max_power_store = 0
    sql2 = "INSERT INTO energy_daily (day_ordinal, production, import, export, max_power_production,max_power_import,max_power_export,max_power_consumption,max_power_use,max_power_store) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    for entry in energy_data:
        id, dat, prod, imp, exp, power_production, power_import, power_export = entry
        while dat > (datetime.combine(start_date, time()) + timedelta(days=1)).timestamp():
            db_con.execute(sql2, (start_date.toordinal(), production, import_,export,max_power_production,max_power_import,max_power_export,max_power_consumption,max_power_use,max_power_store))
            max_power_production = 0
            max_power_import = 0
            max_power_export = 0
            max_power_consumption = 0
            max_power_use = 0
            max_power_store = 0
            start_date += timedelta(days=1)

        max_power_production = max(max_power_production, power_production)
        max_power_import = max(max_power_import, power_import)
        max_power_export = max(max_power_export, power_export)
        max_power_consumption = max(max_power_consumption, power_import + power_production - power_export)
        max_power_use = max(max_power_use, power_production - power_export)
        max_power_store = int(max(max_power_store, power_export * 0.8 - power_import))
        production = prod
        import_ = imp
        export = exp

    if date.today() > start_date:
        db_con.execute(sql2, (start_date.toordinal(), production, import_,export,max_power_production,max_power_import,max_power_export,max_power_consumption,max_power_use,max_power_store))

    db_con.commit()
    db_con.close()


if __name__ == '__main__':
    main()
