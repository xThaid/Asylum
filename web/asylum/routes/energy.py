import datetime

from flask import render_template, jsonify, make_response, redirect, url_for

from asylum.core import energy_data
from asylum.core.auth import authorize
from asylum.core.utilities import add_month
from asylum.core.chart_data import ChartData
from asylum.core.page_model import PageModel
from asylum.models.energy import Energy, EnergyDaily

MIN_DATE = datetime.date(2018, 6, 21)


def init_energy_routes(app):
    @app.route('/energy')
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

    @app.route('/energy/history')
    @authorize('guest', 'user', 'admin')
    def energy_history_redirect(context):
        return redirect(url_for("energy_now"), code=302)

    @app.route('/energy/history/day', defaults={'date': None, 'page': 'energy'})
    @app.route('/energy/history/day_<string:page>', defaults={'date': None})
    @app.route('/energy/history/day/<string:date>', defaults={'page': 'energy'})
    @app.route('/energy/history/day/<string:date>_<string:page>',)
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
            .add_breadcrumb_page('Historia dnia', '/energy/history/day') \
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
            'active_tab': active_tab_index
        }
        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/history/month', defaults={'date': None, 'page': 'energy'})
    @app.route('/energy/history/month_<string:page>', defaults={'date': None})
    @app.route('/energy/history/month/<string:date>', defaults={'page': 'energy'})
    @app.route('/energy/history/month/<string:date>_<string:page>',)
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
            to_date = add_month(from_date) - datetime.timedelta(days=1)
        except ValueError:
            return redirect(url_for('energy_history_month'), code=302)

        if MIN_DATE.year > from_date.year or (MIN_DATE.year == from_date.year and MIN_DATE.month > from_date.month) or from_date > datetime.date.today():
            return redirect(url_for('energy_history_month'), code=302)

        if page not in ['energy', 'charts', 'records']:
            return redirect(url_for('energy_history_month', date=date), code=302)

        active_tab_index = 0
        if page == 'energy':
            active_tab_index = 1
        elif page == 'charts':
            active_tab_index = 2
        elif page == 'records':
            active_tab_index = 3

        page_model = PageModel('Energia - historia miesiąca ' + date_temp, context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .add_breadcrumb_page('Historia miesiąca', '') \
            .add_tab('Energia', tab_url) \
            .add_tab('Wykresy', tab_url + '_charts') \
            .add_tab('Rekordy', tab_url + '_records') \
            .activate_tab(active_tab_index) \
            .to_dict()

        query_result = EnergyDaily.get_last_rows(from_date - datetime.timedelta(days=1), to_date)

        days_in_month = (to_date - from_date).days + 1

        productions_per_day = [0] * days_in_month
        consumptions_per_day = [0] * days_in_month
        uses_per_day = [0] * days_in_month
        imports_per_day = [0] * days_in_month
        exports_per_day = [0] * days_in_month
        storeds_per_day = [0] * days_in_month

        for x in query_result[1:]:
            index = datetime.date.fromordinal(x.day_ordinal).day - 1
            productions_per_day[index] = round(x.production / 1000, 2)
            consumptions_per_day[index] = round((x.import_ + x.production - x.export) / 1000, 2)
            uses_per_day[index] = round((x.production - x.export) / 1000, 2)
            imports_per_day[index] = round(x.import_ / 1000, 2)
            exports_per_day[index] = round(x.export / 1000, 2)
            storeds_per_day[index] = round(((x.export * 0.8) - x.import_) / 1000, 2)

        daily_production = 0
        daily_import = 0
        daily_export = 0

        if add_month(from_date) > datetime.date.today():
            daily_frist = Energy.get_last_rows(datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(), datetime.datetime.now().timestamp(), 1)
            daily_last = Energy.get_last_rows(datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(),datetime.datetime.now().timestamp(), 1, True)
            daily_production = daily_last[0].production - daily_frist[0].production
            daily_import = daily_last[0].import_ - daily_frist[0].import_
            daily_export = daily_last[0].export - daily_frist[0].export
            index = datetime.date.today().day - 1
            productions_per_day[index] = round(daily_production / 1000, 2)
            consumptions_per_day[index] = round((daily_import + daily_production - daily_export) / 1000, 2)
            uses_per_day[index] = round((daily_production - daily_export) / 1000, 2)
            imports_per_day[index] = round(daily_import / 1000, 2)
            exports_per_day[index] = round(daily_export / 1000, 2)
            storeds_per_day[index] = round(((daily_export * 0.8) - daily_import) / 1000, 2)

        production_total = round((query_result[-1].production_offset - query_result[0].production_offset + daily_production) / 1000, 2)
        import_total = round((query_result[-1].import_offset - query_result[0].import_offset + daily_import) / 1000, 2)
        export_total = round((query_result[-1].export_offset - query_result[0].export_offset + daily_export) / 1000, 2)
        uses_total = production_total - export_total
        consumption_total = import_total + uses_total
        stored_total = round(export_total * 0.8 - import_total, 2)

        chart_labels = []
        for x in range(days_in_month):
            chart_labels.append(from_date + datetime.timedelta(days=x))

        energy_chart_data = ChartData() \
            .set_labels([x.strftime('%d') for x in chart_labels]) \
            .add_dataset('Produkcja', productions_per_day, [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', consumptions_per_day, [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', uses_per_day, [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', imports_per_day, [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', exports_per_day, [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', storeds_per_day, [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()

        max_productions = []
        max_consumptions = []
        max_imports = []
        max_exports = []
        max_uses = []
        max_stores = []
        for x in range(1, len(query_result)):
            max_productions.append(query_result[x].max_power_production)
            max_imports.append(query_result[x].max_power_import)
            max_exports.append(query_result[x].max_power_export)
            max_consumptions.append(query_result[x].max_power_consumption)
            max_uses.append(query_result[x].max_power_use)
            max_stores.append(query_result[x].max_power_store)

        records = {
            'max_power': {
                'production': {
                    'value': max(max_productions),
                    'day': chart_labels[max_productions.index(max(max_productions))],
                },
                'consumption': {
                    'value': max(max_consumptions),
                    'day': chart_labels[max_consumptions.index(max(max_consumptions))],
                },
                'import': {
                    'value': max(max_imports),
                    'day': chart_labels[max_imports.index(max(max_imports))],
                },
                'export': {
                    'value': max(max_exports),
                    'day': chart_labels[max_exports.index(max(max_exports))],
                },
                'use': {
                    'value': max(max_uses),
                    'day': chart_labels[max_uses.index(max(max_uses))],
                },
                'store': {
                    'value': max(max_stores),
                    'day': chart_labels[max_stores.index(max(max_stores))],
                },
            },
            'max_energy': {
                'production': {
                    'value': max(productions_per_day),
                    'day': chart_labels[productions_per_day.index(max(productions_per_day))]
                },
                'consumption': {
                    'value': max(consumptions_per_day),
                    'day': chart_labels[consumptions_per_day.index(max(consumptions_per_day))],
                },
                'import': {
                    'value': max(imports_per_day),
                    'day': chart_labels[imports_per_day.index(max(imports_per_day))],
                },
                'export': {
                    'value': max(exports_per_day),
                    'day': chart_labels[exports_per_day.index(max(exports_per_day))],
                },
                'use': {
                    'value': max(uses_per_day),
                    'day': chart_labels[uses_per_day.index(max(uses_per_day))],
                },
                'store': {
                    'value': max(storeds_per_day),
                    'day': chart_labels[storeds_per_day.index(max(storeds_per_day))],
                },
            }
        }

        data_model = {
            'energy_production': productions_per_day,
            'energy_production_total': production_total,
            'energy_consumption': consumptions_per_day,
            'energy_consumption_total': consumption_total,
            'energy_use': uses_per_day,
            'energy_use_total': uses_total,
            'energy_import': imports_per_day,
            'energy_import_total': import_total,
            'energy_export': exports_per_day,
            'energy_export_total': export_total,
            'energy_stored': storeds_per_day,
            'energy_stored_total': stored_total,
            'power_chart_data': None,
            'energy_chart_data': energy_chart_data,
            'isDayHistory': False,
            'records': records,
            'active_tab': active_tab_index
        }
        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/history/year', defaults={'date': None, 'page': 'energy'})
    @app.route('/energy/history/year_<string:page>', defaults={'date': None})
    @app.route('/energy/history/year/<string:date>', defaults={'page': 'energy'})
    @app.route('/energy/history/year/<string:date>_<string:page>',)
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
            to_date = from_date.replace(year=from_date.year + 1) - datetime.timedelta(days=1)
        except ValueError:
            return redirect(url_for('energy_history_year'), code=302)

        if MIN_DATE.year > from_date.year or from_date.year > datetime.date.today().year:
            return redirect(url_for('energy_history_year'), code=302)

        if page not in ['energy', 'charts', 'records']:
            return redirect(url_for('energy_history_year', date=date), code=302)

        active_tab_index = 0
        if page == 'energy':
            active_tab_index = 1
        elif page == 'charts':
            active_tab_index = 2
        elif page == 'records':
            active_tab_index = 3

        page_model = PageModel('Energia - historia roku ' + date_temp, context['user']) \
            .add_breadcrumb_page('Energia', '/energy/now') \
            .add_breadcrumb_page('Historia roku', '') \
            .add_tab('Energia', tab_url) \
            .add_tab('Wykresy', tab_url + '_charts') \
            .add_tab('Rekordy', tab_url + '_records') \
            .activate_tab(active_tab_index) \
            .to_dict()

        query_result = EnergyDaily.get_last_rows(from_date - datetime.timedelta(days=1), to_date)

        productions_per_month = [0] * 12
        consumptions_per_month = [0] * 12
        uses_per_month = [0] * 12
        imports_per_month = [0] * 12
        exports_per_month = [0] * 12
        storeds_per_month = [0] * 12

        previous_month = query_result[0]
        for x in query_result[1:]:
            if datetime.date.fromordinal(x.day_ordinal + 1).day == 1:
                month_index = datetime.date.fromordinal(x.day_ordinal).month - 1
                productions_per_month[month_index] = round((x.production_offset - previous_month.production_offset) / 1000, 2)
                imports_per_month[month_index] = round((x.import_offset - previous_month.import_offset) / 1000, 2)
                exports_per_month[month_index] = round((x.export_offset - previous_month.export_offset) / 1000, 2)
                uses_per_month[month_index] = round(productions_per_month[month_index] - exports_per_month[month_index], 2)
                consumptions_per_month[month_index] = round(imports_per_month[month_index] + uses_per_month[month_index], 2)
                storeds_per_month[month_index] = round(exports_per_month[month_index] * 0.8 - imports_per_month[month_index], 2)
                previous_month = x

        month_index = datetime.date.fromordinal(query_result[-1].day_ordinal).month - 1
        if not (month_index == (datetime.date.fromordinal(previous_month.day_ordinal).month - 1)):
            productions_per_month[month_index] = round((query_result[-1].production_offset - previous_month.production_offset) / 1000, 2)
            imports_per_month[month_index] = round((query_result[-1].import_offset - previous_month.import_offset) / 1000, 2)
            exports_per_month[month_index] = round((query_result[-1].export_offset - previous_month.export_offset) / 1000, 2)
            uses_per_month[month_index] = round(productions_per_month[month_index] - exports_per_month[month_index], 2)
            consumptions_per_month[month_index] = round(imports_per_month[month_index] + uses_per_month[month_index], 2)
            storeds_per_month[month_index] = round(exports_per_month[month_index] * 0.8 - imports_per_month[month_index], 2)

        daily_production = 0
        daily_import = 0
        daily_export = 0

        if from_date.replace(year=from_date.year + 1) > datetime.date.today():
            daily_frist = Energy.get_last_rows(datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(), datetime.datetime.now().timestamp(), 1)
            daily_last = Energy.get_last_rows(datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(), datetime.datetime.now().timestamp(), 1, True)
            daily_production = daily_last[0].production - daily_frist[0].production
            daily_import = daily_last[0].import_ - daily_frist[0].import_
            daily_export = daily_last[0].export - daily_frist[0].export
            index = datetime.date.today().month - 1
            productions_per_month[index] = round((daily_production / 1000) + productions_per_month[index], 2)
            consumptions_per_month[index] = round(((daily_import + daily_production - daily_export) / 1000) + consumptions_per_month[index], 2)
            uses_per_month[index] = round(((daily_production - daily_export) / 1000) + uses_per_month[index], 2)
            imports_per_month[index] = round((daily_import / 1000) + imports_per_month[index], 2)
            exports_per_month[index] = round((daily_export / 1000) + exports_per_month[index], 2)
            storeds_per_month[index] = round((((daily_export * 0.8) - daily_import) / 1000) + storeds_per_month[index], 2)

        production_total = round((query_result[-1].production_offset - (query_result[0].production_offset if not from_date.year == 2018 else 0) + daily_production) / 1000, 2)
        import_total = round((query_result[-1].import_offset - (query_result[0].import_offset if not from_date.year == 2018 else 0) + daily_import) / 1000, 2)
        export_total = round((query_result[-1].export_offset - (query_result[0].export_offset if not from_date.year == 2018 else 0) + daily_export) / 1000, 2)
        uses_total = production_total - export_total
        consumption_total = import_total + uses_total
        stored_total = round(export_total * 0.8 - import_total, 2)

        chart_labels = []
        for x in range(12):
            chart_labels.append(str(x + 1))

        energy_chart_data = ChartData() \
            .set_labels(chart_labels) \
            .add_dataset('Produkcja', productions_per_month, [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', consumptions_per_month, [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', uses_per_month, [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', imports_per_month, [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', exports_per_month, [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', storeds_per_month, [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()

        max_productions = []
        max_consumptions = []
        max_imports = []
        max_exports = []
        max_uses = []
        max_stores = []

        productions_per_day = []
        consumptions_per_day = []
        uses_per_day = []
        imports_per_day = []
        exports_per_day = []
        storeds_per_day = []

        days = []

        for x in query_result:
            max_productions.append(x.max_power_production)
            max_consumptions.append(x.max_power_consumption)
            max_imports.append(x.max_power_import)
            max_exports.append(x.max_power_export)
            max_uses.append(x.max_power_use)
            max_stores.append(x.max_power_store)

            productions_per_day.append(x.production / 1000)
            imports_per_day.append(x.import_ / 1000)
            exports_per_day.append(x.export / 1000)
            uses_per_day.append((x.production - x.export) / 1000)
            consumptions_per_day.append((x.import_ / 1000) + uses_per_day[-1])
            storeds_per_day.append((x.export * 0.8 - x.import_) / 1000)

            days.append(datetime.date.fromordinal(x.day_ordinal).strftime('%Y-%m-%d'))

        max_production = max(max_productions)
        max_consumption = max(max_consumptions)
        max_import = max(max_imports)
        max_export = max(max_exports)
        max_store = max(max_stores)
        max_use = max(max_uses)

        max_energy_production = max(productions_per_day)
        max_energy_consumption = max(consumptions_per_day)
        max_energy_import = max(imports_per_day)
        max_energy_export = max(exports_per_day)
        max_energy_use = max(uses_per_day)
        max_energy_store = max(storeds_per_day)

        records = {
            'max_power': {
                'production': {
                    'value': max_production,
                    'day': days[max_productions.index(max_production)],
                },
                'consumption': {
                    'value': max_consumption,
                    'day': days[max_consumptions.index(max_consumption)],
                },
                'import': {
                    'value': max_import,
                    'day': days[max_imports.index(max_import)],
                },
                'export': {
                    'value': max_export,
                    'day': days[max_exports.index(max_export)],
                },
                'use': {
                    'value': max_use,
                    'day': days[max_uses.index(max_use)],
                },
                'store': {
                    'value': max_store,
                    'day': days[max_stores.index(max_store)],
                },
            },
            'max_energy': {
                'production': {
                    'value': max_energy_production,
                    'day': days[productions_per_day.index(max_energy_production)]
                },
                'consumption': {
                    'value': max_energy_consumption,
                    'day': days[consumptions_per_day.index(max_energy_consumption)]
                },
                'import': {
                    'value': max_energy_import,
                    'day': days[imports_per_day.index(max_energy_import)]
                },
                'export': {
                    'value': max_energy_export,
                    'day': days[exports_per_day.index(max_energy_export)]
                },
                'use': {
                    'value': max_energy_use,
                    'day': days[uses_per_day.index(max_energy_use)]
                },
                'store': {
                    'value': max_energy_store,
                    'day': days[storeds_per_day.index(max_energy_store)]
                },
            }
        }

        data_model = {
            'energy_production': productions_per_month,
            'energy_production_total': production_total,
            'energy_consumption': consumptions_per_month,
            'energy_consumption_total': consumption_total,
            'energy_use': uses_per_month,
            'energy_use_total': uses_total,
            'energy_import': imports_per_month,
            'energy_import_total': import_total,
            'energy_export': exports_per_month,
            'energy_export_total': export_total,
            'energy_stored': storeds_per_month,
            'energy_stored_total': stored_total,
            'power_chart_data': None,
            'energy_chart_data': energy_chart_data,
            'isDayHistory': False,
            'records': records,
            'active_tab': active_tab_index
        }
        return render_template('energy/history.html', data_model=data_model, page_model=page_model)

    @app.route('/energy/history/all')
    @authorize('guest', 'user', 'admin')
    def energy_history_all(context):
        return redirect(url_for("energy_history_year"), code=302)

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
