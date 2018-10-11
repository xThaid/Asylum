from flask import render_template, jsonify, make_response
from datetime import datetime, timedelta
import operator

from asylum.core import energy_data
from asylum.core.page_model import PageModel
from asylum.core.chart_data import ChartData
from asylum.core.auth import authorize
from asylum.models.energy import Energy


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def energy(context):
        page_model = PageModel('Energia', context['user'])\
            .add_breadcrumb_page('Energia', '/energy')\
            .add_tab('Statystyki')\
            .add_tab('Wykresy') \
            .to_dict()

        start_time = datetime.now().replace(hour=0, minute=0, second=0)
        data = Energy.get_last_rows(start_time.timestamp())
        grouped_data = []
        for x in range(datetime.now().hour + 1):
            grouped_data.append([])
        curr_hour = 0
        next_time = start_time + timedelta(hours=1)
        for entry in data:
            while entry.time >= next_time.timestamp():
                curr_hour += 1
                next_time = next_time + timedelta(hours=1)
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

        time_from_midnight = datetime.now().timestamp() - datetime.now().replace(hour=0, minute=0, second=0).timestamp()
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

        chart_time_points = [(start_time + timedelta(minutes=x*chart_time_separation))
                             for x in range(chart_points_count)]

        grouped_data = []
        for x in range(int((datetime.now().hour * 60 + datetime.now().minute)/chart_time_separation) + 1):
            grouped_data.append([])
        curr_time = 0
        next_time = start_time + timedelta(minutes=chart_time_separation)

        for entry in data:
            while entry.time >= next_time.timestamp():
                curr_time += 1
                next_time = next_time + timedelta(minutes=chart_time_separation)
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
                    chart_power['export']\
                        .append(int(max(map(lambda x: x.power_export, x))))
                    chart_power['import']\
                        .append(int(max(map(lambda x: x.power_import, x))))
                    chart_power['production']\
                        .append(int(max(map(lambda x: x.power_production, x))))

                    chart_power['use'].append(max(0, chart_power['production'][-1] - chart_power['export'][-1]))
                    chart_power['store'].append(int(chart_power['export'][-1] * 0.8 - chart_power['import'][-1]))
                    chart_power['consumption'].append(chart_power['use'][-1] + chart_power['import'][-1])
                else:
                    for y in chart_power:
                        chart_power[y].append(None)

        power_chart_data = ChartData()\
            .set_labels([x.strftime('%H:%M') for x in chart_time_points])\
            .add_dataset('Produkcja', chart_power['production'], [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', chart_power['consumption'],  [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', chart_power['use'], [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', chart_power['import'], [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', chart_power['export'], [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', chart_power['store'], [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()
        energy_chart_labels = []
        for x in range(datetime.now().hour + 1):
            temp = ""
            if x < 10:
                temp = "0"
            energy_chart_labels.append(temp + str(x) + ":00")

        energy_chart_data = ChartData()\
            .set_labels(energy_chart_labels)\
            .add_dataset('Produkcja', productions, [25, 180, 25, 1], [50, 200, 50, 0.2]) \
            .add_dataset('Zużycie', consumptions,  [210, 15, 15, 1], [230, 30, 30, 0.2]) \
            .add_dataset('Wykorzystanie', uses, [5, 5, 231, 1], [25, 25, 250, 0.2], True) \
            .add_dataset('Pobieranie', imports, [100, 100, 5, 1], [230, 230, 30, 0.2], True) \
            .add_dataset('Oddawanie', exports, [30, 190, 190, 1], [50, 210, 210, 0.2], True) \
            .add_dataset('Magazynowanie', storeds, [140, 30, 100, 1], [180, 60, 130, 0.2], True) \
            .to_json()

        power_production_list = list(filter(lambda x: x is not None, list(map(lambda x: x.power_production, data))))
        power_import_list = list(filter(lambda x: x is not None, list(map(lambda x: x.power_import, data))))
        power_export_list = list(filter(lambda x: x is not None, list(map(lambda x: x.power_export, data))))

        if len(power_production_list) == 0:
            max_production = 0
            max_consumption = 0
        else:
            max_production = max(power_production_list)
            max_consumption = max(list(map(
                operator.add, list(map(operator.sub, power_production_list, power_export_list)), power_import_list
            )))

        data_model = {
            'power_production_average': int(production_delta * 3600 / time_from_midnight),
            'power_production_max': int(max_production),
            'energy_production': productions,
            'energy_production_total': production_delta / 1000,
            'power_consumption_average': int(consumption_delta * 3600 / time_from_midnight),
            'power_consumption_max': int(max_consumption),
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
            'energy_chart_data': energy_chart_data
        }
        return render_template('energy.html', page_model=page_model, data_model=data_model)

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
