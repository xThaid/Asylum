import datetime
from calendar import monthrange

from flask import render_template, jsonify, make_response, redirect, url_for

from asylum.energy import energy_data
from asylum.web.core.auth import authorize
from asylum.web.core.chart_data import ChartData, EnergyRecords
from asylum.web.core.page_model import PageModel
from asylum.web.models.energy import Energy, EnergyDaily

MIN_DATE = datetime.date(2018, 6, 21)


def init_energy_routes(app):
    @app.route('/energy')
    @app.route('/energy/')
    @authorize('guest', 'user', 'admin')
    def energy_redirect(context):
        return redirect(url_for('energy_now'), code=302)

    @app.route('/energy/now', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def energy_now(context):
        page_model = PageModel('Energia - strona główna', context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .to_dict()
        data_model = {
            'MIN_DATE': MIN_DATE.strftime('%Y-%m-%d')
        }
        return render_template('energy/now.html', page_model=page_model, data_model=data_model)


    @app.route('/energy/day', defaults={'date': None, 'page': 'energy'})
    @app.route('/energy/day_<string:page>', defaults={'date': None})
    @app.route('/energy/day/<string:date>', defaults={'page': 'energy'})
    @app.route('/energy/day/<string:date>_<string:page>',)
    @authorize('guest', 'user', 'admin')
    def energy_history_day(context, date, page):
        if date is None:
            date_temp = datetime.datetime.now().strftime('%Y-%m-%d')
            tab_url = "day"
        else:
            date_temp = date
            tab_url = date
        try:
            start_time = datetime.datetime.strptime(date_temp, '%Y-%m-%d')
        except ValueError:
            return redirect(url_for('energy_history_day'), code=302)

        if MIN_DATE > start_time.date() or start_time.date() > datetime.date.today():
            return redirect(url_for('energy_history_day'), code=302)

        if page not in ['energy', 'charts']:
            return redirect(url_for('energy_history_day', date=date), code=302)

        active_tab_index = 0
        if page == 'energy':
            active_tab_index = 1
        elif page == 'charts':
            active_tab_index = 2

        page_model = PageModel('Energia - historia dnia ' + date_temp, context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .add_breadcrumb_page('Historia dnia', '/energy/day') \
            .add_tab('Energia', tab_url) \
            .add_tab('Wykresy', tab_url + '_charts') \
            .activate_tab(active_tab_index) \
            .to_dict()

        data = Energy.get_last_rows(start_time.timestamp(), (start_time + datetime.timedelta(days=1)).timestamp())
        grouped_data = []
        for x in range(datetime.datetime.now().hour + 1 if
                       (start_time + datetime.timedelta(days=1)) > datetime.datetime.now() else 24):
            grouped_data.append([])
        curr_hour = 0
        next_time = start_time + datetime.timedelta(hours=1)
        for entry in data:
            while entry.time >= next_time.timestamp():
                curr_hour += 1
                next_time = next_time + datetime.timedelta(hours=1)
            grouped_data[curr_hour].append(entry)

        productions = []
        imports = []
        exports = []
        consumptions = []
        uses = []
        storeds = []
        for group in grouped_data:
            if len(group) == 0:
                prod = imp = exp = 0
            else:
                prod = (group[-1].production - group[0].production) / 1000
                imp = (group[-1].import_ - group[0].import_) / 1000
                exp = (group[-1].export - group[0].export) / 1000

            productions.append(round(prod, 2))
            imports.append(round(imp, 2))
            exports.append(round(exp, 2))

            consumptions.append(round(prod - exp + imp, 2))
            uses.append(round(prod - exp, 2))
            storeds.append(round(exp * 0.8 - imp, 2))

        if (start_time + datetime.timedelta(days=1)) > datetime.datetime.now():
            time_from_midnight = (datetime.datetime.now().timestamp() -
                                  datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp())
        else:
            time_from_midnight = 24 * 60 * 60

        if time_from_midnight == 0:
            time_from_midnight = 1

        if len(data) == 0:
            production_delta = import_delta = export_delta = 0
        else:
            production_delta = data[-1].production - data[0].production
            import_delta = data[-1].import_ - data[0].import_
            export_delta = data[-1].export - data[0].export

        consumption_delta = production_delta - export_delta + import_delta
        use_delta = production_delta - export_delta
        stored_delta = export_delta * 0.8 - import_delta

        chart_time_separation = 4
        chart_points_count = int(time_from_midnight / (60 * chart_time_separation)) + 1

        chart_time_points = [(start_time + datetime.timedelta(minutes=x * chart_time_separation))
                             for x in range(chart_points_count)]

        grouped_data = []
        if (start_time + datetime.timedelta(days=1)) > datetime.datetime.now():
            power_chart_group_count = int(
                (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) / chart_time_separation) + 1
        else:
            power_chart_group_count = int((24 * 60) / chart_time_separation) + 1

        for x in range(power_chart_group_count):
            grouped_data.append([])
        curr_time = 0
        next_time = start_time + datetime.timedelta(minutes=chart_time_separation)

        for entry in data:
            while entry.time >= next_time.timestamp():
                curr_time += 1
                next_time = next_time + datetime.timedelta(minutes=chart_time_separation)
            grouped_data[curr_time].append(entry)

        chart_power = {
            'production': [],
            'consumption': [],
            'import': [],
            'export': [],
            'use': [],
            'store': []
        }
        if len(data) > 0:
            for x in grouped_data:
                if len(x) > 0:
                    chart_power['export'].append(int(max(map(lambda x: x.power_export, x))))
                    chart_power['import'].append(int(max(map(lambda x: x.power_import, x))))
                    chart_power['production'].append(int(max(map(lambda x: x.power_production, x))))

                    chart_power['use'].append(max(0, int(max(map(lambda x: x.power_production - x.power_export, x)))))
                    chart_power['store'].append(int(max(map(lambda x: (x.power_export * 0.8) - x.power_import, x))))
                    chart_power['consumption'].append(int(max(
                        map(lambda x: x.power_production - x.power_export + x.power_import, x))))
                else:
                    for y in chart_power:
                        chart_power[y].append(None)

        power_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in chart_time_points]) \
            .add_dataset('Produkcja', chart_power['production'], [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', chart_power['consumption'], [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', chart_power['use'], [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', chart_power['import'], [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', chart_power['export'], [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', chart_power['store'], [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()

        energy_chart_labels = []
        for x in range(datetime.datetime.now().hour + 1 if
                       (start_time + datetime.timedelta(days=1)) > datetime.datetime.now() else 24):
            temp = ""
            if x < 10:
                temp = "0"
            energy_chart_labels.append(temp + str(x) + ":00")

        energy_chart_data = ChartData() \
            .set_labels(energy_chart_labels) \
            .add_dataset('Produkcja', productions, [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', consumptions, [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', uses, [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', imports, [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', exports, [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', storeds, [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()

        data_model = {
            'energy_production': productions,
            'energy_production_total': production_delta / 1000,
            'energy_consumption': consumptions,
            'energy_consumption_total': consumption_delta / 1000,
            'energy_use': uses,
            'energy_use_total': use_delta / 1000,
            'energy_import': imports,
            'energy_import_total': import_delta / 1000,
            'energy_export': exports,
            'energy_export_total': export_delta / 1000,
            'energy_stored': storeds,
            'energy_stored_total': stored_delta / 1000,
            'power_chart_data': power_chart_data,
            'energy_chart_data': energy_chart_data,
            'is_day_history': True,
            'active_tab': page
        }
        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/month', defaults={'date': None, 'page': 'energy'})
    @app.route('/energy/month_<string:page>', defaults={'date': None})
    @app.route('/energy/month/<string:date>', defaults={'page': 'energy'})
    @app.route('/energy/month/<string:date>_<string:page>',)
    @authorize('guest', 'user', 'admin')
    def energy_history_month(context, date, page):
        if date is None:
            date_temp = datetime.datetime.now().strftime('%Y-%m')
            tab_url = 'month'
        else:
            date_temp = date
            tab_url = date
        try:
            from_date = datetime.datetime.strptime(date_temp, '%Y-%m').date()
        except ValueError:
            return redirect(url_for('energy_history_month'), code=302)

        if MIN_DATE.year > from_date.year or (MIN_DATE.year == from_date.year and MIN_DATE.month > from_date.month) or from_date > datetime.date.today():
            return redirect(url_for('energy_history_month'), code=302)

        if page not in ['energy', 'charts', 'records']:
            return redirect(url_for('energy_history_month', date=date), code=302)

        tab_mapping = {'energy': 1, 'charts': 2, 'records': 3}
        page_model = PageModel('Energia - historia miesiąca ' + date_temp, context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .add_breadcrumb_page('Historia miesiąca', '') \
            .add_tab('Energia', tab_url) \
            .add_tab('Wykresy', tab_url + '_charts') \
            .add_tab('Rekordy', tab_url + '_records') \
            .activate_tab(tab_mapping[page]) \
            .to_dict()

        data_model = aggregate_energy_data(from_date, 'month')
        data_model.update({
            'power_chart_data': None,
            'isDayHistory': False,
            'active_tab': page
        })

        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/year', defaults={'date': None, 'page': 'energy'})
    @app.route('/energy/year_<string:page>', defaults={'date': None})
    @app.route('/energy/year/<string:date>', defaults={'page': 'energy'})
    @app.route('/energy/year/<string:date>_<string:page>',)
    @authorize('guest', 'user', 'admin')
    def energy_history_year(context, date, page):
        if date is None:
            date_temp = datetime.datetime.now().strftime('%Y')
            tab_url = 'year'
        else:
            date_temp = date
            tab_url = date
        try:
            from_date = datetime.datetime.strptime(date_temp, '%Y').date()
        except ValueError:
            return redirect(url_for('energy_history_year'), code=302)

        if MIN_DATE.year > from_date.year or from_date.year > datetime.date.today().year:
            return redirect(url_for('energy_history_year'), code=302)

        if page not in ['energy', 'charts', 'records']:
            return redirect(url_for('energy_history_year', date=date), code=302)

        tab_mapping = {'energy': 1, 'charts': 2, 'records': 3}
        page_model = PageModel('Energia - historia roku ' + date_temp, context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .add_breadcrumb_page('Historia roku', '') \
            .add_tab('Energia', tab_url) \
            .add_tab('Wykresy', tab_url + '_charts') \
            .add_tab('Rekordy', tab_url + '_records') \
            .activate_tab(tab_mapping[page]) \
            .to_dict()

        data_model = aggregate_energy_data(from_date, 'year')
        data_model.update({
            'power_chart_data': None,
            'isDayHistory': False,
            'active_tab': page
        })

        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/all', defaults={'page': 'energy'})
    @app.route('/energy/all_<string:page>',)
    @authorize('guest', 'user', 'admin')
    def energy_history_all(context, page):
        if page not in ['energy', 'charts', 'records']:
            return redirect(url_for('energy_history_all'), code=302)

        tab_mapping = {'energy': 1, 'charts': 2, 'records': 3}
        page_model = PageModel('Energia - cała historia ', context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .add_breadcrumb_page('Cała historia', '') \
            .add_tab('Energia', 'all') \
            .add_tab('Wykresy', 'all' + '_charts') \
            .add_tab('Rekordy', 'all' + '_records') \
            .activate_tab(tab_mapping[page]) \
            .to_dict()

        MONTHLY = True

        data_model = aggregate_energy_data(MIN_DATE, 'all_monthly' if MONTHLY else 'all')
        data_model.update({
            'power_chart_data': None,
            'isDayHistory': False,
            'active_tab': page
        })

        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/getCurrentPowerData', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def get_current_power_data(context):
        current_data = energy_data.get_data()

        if current_data is None:
            return make_response('', 500)

        return jsonify({
            'production': current_data['power_production'],
            'consumption': current_data['power_consumption'],
            'use': current_data['power_use'],
            'import': current_data['power_import'],
            'export': current_data['power_export'],
            'store': current_data['power_store']
        })

    def aggregate_energy_data(from_date, type):
        if type == 'month':
            to_date = from_date.replace(day=monthrange(from_date.year, from_date.month)[1])
        elif type == 'year':
            to_date = from_date.replace(year=from_date.year + 1) - datetime.timedelta(days=1)
        elif type == 'all' or type == 'all_monthly':
            to_date = datetime.date.today()

        raw_data = EnergyDaily.get_last_rows(from_date - datetime.timedelta(days=1), to_date)

        # We have to make sure that very first day of measurements is also counted
        if raw_data[0].id == 1:
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

        # Add data from current day
        current_day_first_entry = Energy.get_last_rows(datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(), datetime.datetime.now().timestamp(), 1)
        current_day_last_entry = Energy.get_last_rows(datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(), datetime.datetime.now().timestamp(), 1, True)
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
            if (type == 'month' and from_date.month == datetime.date.today().month) or \
               (type == 'year' and from_date.year == datetime.date.today().year) or \
               (type == 'all' or type == 'all_monthly'):
                raw_data.append(current_day_data)

        # Calculate total energy
        total_energy_production = round((raw_data[-1].production_offset - raw_data[0].production_offset) / 1000, 2)
        total_energy_import = round((raw_data[-1].import_offset - raw_data[0].import_offset) / 1000, 2)
        total_energy_export = round((raw_data[-1].export_offset - raw_data[0].export_offset) / 1000, 2)
        total_energy_use = round(total_energy_production - total_energy_export, 2)
        total_energy_consumption = round(total_energy_import + total_energy_use, 2)
        total_energy_store = round(total_energy_export * 0.8 - total_energy_import, 2)

        # Aggregate data
        if type == 'month':
            aggregation_size = to_date.day - from_date.day + 1
        elif type == 'year':
            aggregation_size = 12
        elif type == 'all':
            aggregation_size = to_date.year - from_date.year + 1
        elif type == 'all_monthly':
            aggregation_size = (to_date.year - from_date.year + 1) * 12

        aggregated_production = [0] * aggregation_size
        aggregated_import = [0] * aggregation_size
        aggregated_export = [0] * aggregation_size
        aggregated_consumption = [0] * aggregation_size
        aggregated_use = [0] * aggregation_size
        aggregated_store = [0] * aggregation_size

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
        max_daily_use = (0, 0)
        max_daily_store = (-1000, 0)

        previous_data = raw_data[0]
        for x in raw_data[1:]:
            next_day_date = datetime.date.fromordinal(x.day_ordinal + 1)
            if (x.day_ordinal == raw_data[-1].day_ordinal) or \
               (type == 'month') or \
               (type == 'year' and next_day_date.day == 1) or \
               (type == 'all' and next_day_date.day == 1 and next_day_date.month == 1) or \
               (type == 'all_monthly' and next_day_date.day == 1):
                current_day_date = datetime.date.fromordinal(x.day_ordinal)
                if type == 'month':
                    idx = current_day_date.day - 1
                elif type == 'year':
                    idx = current_day_date.month - 1
                elif type == 'all':
                    idx = current_day_date.year - from_date.year
                elif type == 'all_monthly':
                    idx = (current_day_date.year - from_date.year) * 12 + current_day_date.month - 1

                if type == 'month':
                    aggregated_production[idx] = round(x.production / 1000, 2)
                    aggregated_import[idx] = round(x.import_ / 1000, 2)
                    aggregated_export[idx] = round(x.export / 1000, 2)
                else:
                    aggregated_production[idx] = round((x.production_offset - previous_data.production_offset) / 1000, 2)
                    aggregated_import[idx] = round((x.import_offset - previous_data.import_offset) / 1000, 2)
                    aggregated_export[idx] = round((x.export_offset - previous_data.export_offset) / 1000, 2)

                aggregated_use[idx] = round(aggregated_production[idx] - aggregated_export[idx], 2)
                aggregated_consumption[idx] = round(aggregated_import[idx] + aggregated_use[idx], 2)
                aggregated_store[idx] = round(aggregated_export[idx] * 0.8 - aggregated_import[idx], 2)
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

        chart_labels = []
        for x in range(aggregation_size):
            if type == 'month':
                label = from_date.replace(day=x + 1).strftime('%d')
            elif type == 'year':
                label = from_date.replace(month=x + 1).strftime('%m')
            elif type == 'all':
                label = from_date.replace(year=from_date.year + x).strftime('%Y')
            elif type == 'all_monthly':
                label = from_date.replace(year=from_date.year + int(x / 12), month=x % 12 + 1).strftime('%m.%y')
            chart_labels.append(label)

        energy_chart_data = ChartData() \
            .set_labels(chart_labels) \
            .add_dataset('Produkcja', aggregated_production, [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', aggregated_consumption, [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', aggregated_use, [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', aggregated_import, [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', aggregated_export, [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', aggregated_store, [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()

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

        data_model = {
            'energy_production': aggregated_production,
            'energy_production_total': total_energy_production,
            'energy_consumption': aggregated_consumption,
            'energy_consumption_total': total_energy_consumption,
            'energy_use': aggregated_use,
            'energy_use_total': total_energy_use,
            'energy_import': aggregated_import,
            'energy_import_total': total_energy_import,
            'energy_export': aggregated_export,
            'energy_export_total': total_energy_export,
            'energy_stored': aggregated_store,
            'energy_stored_total': total_energy_store,
            'energy_chart_data': energy_chart_data,
            'records': records,
        }

        return data_model
