import datetime

from asylum.web.models.energy import EnergyDaily, Energy
from asylum.web.routes.energy import MIN_DATE
from asylum.web.core.chart_data import EnergyRecords
from sqlalchemy import and_

YEAR = 'year'
MONTH = 'month'
DAY = 'day'
MINUTES = 'minutes'

GROUP_SPANS = [YEAR, MONTH, DAY, MINUTES]


def aggregate_energy_data(from_date, to_date, group_span):
    if from_date is None or to_date is None or group_span is None:
        return None
    if group_span not in GROUP_SPANS:
        return None

    if to_date < from_date:
        return None

    raw_data = EnergyDaily.get_last_rows(from_date - datetime.timedelta(days=1), to_date)

    if len(raw_data) == 0:
        return None

    # Add data from current day
    if to_date >= datetime.date.today():
        current_day_first_entry = Energy.get_last_rows(
            datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(),
            datetime.datetime.now().timestamp(), 1)
        current_day_last_entry = Energy.get_last_rows(
            datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(),
            datetime.datetime.now().timestamp(), 1, True)
        if len(current_day_first_entry) != 0:
            current_day_data = EnergyDaily()
            current_day_data.id = 0
            current_day_data.day_ordinal = datetime.date.today().toordinal()
            current_day_data.production = current_day_last_entry[0].production - current_day_first_entry[0].production
            current_day_data.import_ = current_day_last_entry[0].import_ - current_day_first_entry[0].import_
            current_day_data.export = current_day_last_entry[0].export - current_day_first_entry[0].export
            current_day_data.production_offset = current_day_last_entry[0].production
            current_day_data.import_offset = current_day_last_entry[0].import_
            current_day_data.export_offset = current_day_last_entry[0].export
            current_day_data.max_power_production = 0
            current_day_data.max_power_import = 0
            current_day_data.max_power_export = 0
            current_day_data.max_power_consumption = 0
            current_day_data.max_power_use = 0
            current_day_data.max_power_store = 0
            raw_data.append(current_day_data)

    # We have to make sure that very first day of measurements is also counted
    if MIN_DATE >= from_date:
        from_date = MIN_DATE
        dummy_day_data = EnergyDaily()
        dummy_day_data.day_ordinal = raw_data[0].day_ordinal - 1
        dummy_day_data.production = 0
        dummy_day_data.import_ = 0
        dummy_day_data.export = 0
        dummy_day_data.production_offset = 0
        dummy_day_data.import_offset = 0
        dummy_day_data.export_offset = 0
        dummy_day_data.max_power_production = 0
        dummy_day_data.max_power_import = 0
        dummy_day_data.max_power_export = 0
        dummy_day_data.max_power_consumption = 0
        dummy_day_data.max_power_use = 0
        dummy_day_data.max_power_store = 0
        raw_data.insert(0, dummy_day_data)

    # Calculate total energy
    energy_total = {}
    energy_total['production'] = round((raw_data[-1].production_offset - raw_data[0].production_offset) / 1000, 2)
    energy_total['import'] = round((raw_data[-1].import_offset - raw_data[0].import_offset) / 1000, 2)
    energy_total['export'] = round((raw_data[-1].export_offset - raw_data[0].export_offset) / 1000, 2)
    energy_total['use'] = round(energy_total['production'] - energy_total['export'], 2)
    energy_total['consumption'] = round(energy_total['import'] + energy_total['use'], 2)
    energy_total['store'] = round(energy_total['export'] * 0.8 - energy_total['import'], 2)

    # Aggregate data
    aggregated_production = []
    aggregated_import = []
    aggregated_export = []
    aggregated_consumption = []
    aggregated_use = []
    aggregated_store = []

    max_production_power = (0, 0)
    max_import_power = (0, 0)
    max_export_power = (0, 0)
    max_consumption_power = (0, 0)
    max_use_power = (0, 0)
    max_store_power = (0, 0)

    max_daily_production = (0, 0)
    max_daily_import = (0, 0)
    max_daily_export = (0, 0)
    max_daily_consumption = (0, 0)
    max_daily_use = (-1000, 0)
    max_daily_store = (-1000, 0)

    previous_data = raw_data[0]
    for x in raw_data[1:]:
        next_day_date = datetime.date.fromordinal(x.day_ordinal + 1)
        if (x.day_ordinal == raw_data[-1].day_ordinal) or \
                (group_span == DAY) or \
                (group_span == YEAR and next_day_date.day == 1 and next_day_date.month == 1) or \
                (group_span == MONTH and next_day_date.day == 1):

            if group_span == DAY:
                aggregated_production.append(round(x.production / 1000, 2))
                aggregated_import.append(round(x.import_ / 1000, 2))
                aggregated_export.append(round(x.export / 1000, 2))
            else:
                aggregated_production.append(round((x.production_offset - previous_data.production_offset) / 1000, 2))
                aggregated_import.append(round((x.import_offset - previous_data.import_offset) / 1000, 2))
                aggregated_export.append(round((x.export_offset - previous_data.export_offset) / 1000, 2))

            aggregated_use.append(max(0, round(aggregated_production[-1] - aggregated_export[-1], 2)))
            aggregated_consumption.append(round(aggregated_import[-1] + aggregated_use[-1], 2))
            aggregated_store.append(round(aggregated_export[-1] * 0.8 - aggregated_import[-1], 2))
            previous_data = x

        # Calculate daily records
        max_production_power = max(max_production_power, (x.max_power_production, x.day_ordinal))
        max_import_power = max(max_import_power, (x.max_power_import, x.day_ordinal))
        max_export_power = max(max_export_power, (x.max_power_export, x.day_ordinal))
        max_consumption_power = max(max_consumption_power, (x.max_power_consumption, x.day_ordinal))
        max_use_power = max(max_use_power, (x.max_power_use, x.day_ordinal))
        max_store_power = max(max_store_power, (x.max_power_store, x.day_ordinal))

        daily_production = round(x.production / 1000, 2)
        daily_import = round(x.import_ / 1000, 2)
        daily_export = round(x.export / 1000, 2)
        daily_use = round(daily_production - daily_export, 2)
        daily_consumption = round(daily_import + daily_use, 2)
        daily_store = round(daily_export * 0.8 - daily_import, 2)

        max_daily_production = max(max_daily_production, (daily_production, x.day_ordinal))
        max_daily_import = max(max_daily_import, (daily_import, x.day_ordinal))
        max_daily_export = max(max_daily_export, (daily_export, x.day_ordinal))
        max_daily_consumption = max(max_daily_consumption, (daily_consumption, x.day_ordinal))
        max_daily_use = max(max_daily_use, (daily_use, x.day_ordinal))
        max_daily_store = max(max_daily_store, (daily_store, x.day_ordinal))



    records = EnergyRecords() \
        .add_power_record('production', max_production_power) \
        .add_power_record('import', max_import_power) \
        .add_power_record('export', max_export_power) \
        .add_power_record('consumption', max_consumption_power) \
        .add_power_record('use', max_use_power) \
        .add_power_record('store', max_store_power) \
        .add_energy_record('production', max_daily_production) \
        .add_energy_record('import', max_daily_import) \
        .add_energy_record('export', max_daily_export) \
        .add_energy_record('consumption', max_daily_consumption) \
        .add_energy_record('use', max_daily_use) \
        .add_energy_record('store', max_daily_store) \
        .build()

    # In case of groups of minutes we need data from Energy table
    time_separation = 4
    if group_span == MINUTES:
        to_date += datetime.timedelta(days=1)
        if to_date > datetime.date.today():
            to_date = datetime.datetime.now()
        else:
            to_date = datetime.datetime.combine(to_date, datetime.datetime.min.time())

        from_date = datetime.datetime.combine(from_date, datetime.datetime.min.time())

        data = Energy.get_last_rows(from_date.timestamp(), to_date.timestamp())

        if len(data) == 0:
            return None

        grouped_data = []
        group_count = int(((to_date - from_date).total_seconds() / 60) / time_separation)

        for x in range(group_count):
            grouped_data.append([])

        curr_time = 0
        next_time = from_date + datetime.timedelta(minutes=time_separation)

        for entry in data:
            while entry.time >= next_time.timestamp():
                curr_time += 1
                next_time = next_time + datetime.timedelta(minutes=time_separation)
            grouped_data[curr_time].append(entry)

        aggregated_production = []
        aggregated_import = []
        aggregated_export = []
        aggregated_consumption = []
        aggregated_use = []
        aggregated_store = []

        for x in grouped_data:
            production_max = -10000
            import_max = -10000
            export_max = -10000
            consumption_max = -10000
            use_max = -10000
            store_max = -10000

            for y in x:
                production_max = max(production_max, y.power_production)
                import_max = max(import_max, y.power_import)
                export_max = max(export_max, y.power_export)
                use_max = max(use_max, y.power_production - y.power_export)
                consumption_max = max(consumption_max, y.power_import + y.power_production - y.power_export)
                store_max = max(store_max, y.power_export * 0.8 - y.power_import)

            aggregated_production.append(production_max)
            aggregated_import.append(import_max)
            aggregated_export.append(export_max)
            aggregated_consumption.append(consumption_max)
            aggregated_use.append(use_max)
            aggregated_store.append(round(store_max))

    energy_grouped = {
        'production': aggregated_production,
        'consumption': aggregated_consumption,
        'import': aggregated_import,
        'export': aggregated_export,
        'use': aggregated_use,
        'store': aggregated_store
    }

    data = {
        'energy_total': energy_total,
        'energy_grouped': energy_grouped,
        'records': records
    }

    return data
