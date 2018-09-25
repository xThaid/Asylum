from flask import render_template, jsonify, make_response
from datetime import datetime, timedelta

from asylum.core.page_model import PageModel
from asylum.core.auth import authorize
from asylum.core import energy_data
from asylum.models.energy import Energy


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def energy(context):
        page_model = PageModel('Energia', context['user'])\
            .add_breadcrumb_page('Energia', '/energy')\
            .to_dict()

        days_count = 15

        start_time = (datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=days_count - 1))
        data = Energy.get_last_rows(start_time.timestamp())

        grouped_data = [[]]
        curr_day = 0
        next_time = start_time + timedelta(days=1)
        for entry in data:
            if entry.time >= next_time.timestamp():
                curr_day += 1
                next_time = next_time + timedelta(days=1)
                grouped_data.append([])
            grouped_data[curr_day].append(entry)

        productions = []
        imports = []
        exports = []
        consumptions = []
        uses = []
        storeds = []
        for group in grouped_data:
            productions.append((group[-1].production - group[0].production) / 1000)
            imports.append((group[-1].import_ - group[0].import_) / 1000)
            exports.append((group[-1].export - group[0].export) / 1000)
            consumptions.append(productions[-1] - exports[-1] + imports[-1])
            uses.append(productions[-1] - exports[-1])
            storeds.append(exports[-1] * 0.8 - imports[-1])

        time_from_midnight = datetime.now().timestamp() - datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        if time_from_midnight == 0:
            time_from_midnight = 1

        data_model = {
            'power_production_average': int(productions[-1] * 1000 * 3600 / time_from_midnight),
            'power_production_max': 1,
            'energy_production': productions,
            'power_consumption_average': int(consumptions[-1] * 1000 * 3600 / time_from_midnight),
            'power_consumption_max': 1,
            'energy_consumption': consumptions,
            'energy_use': uses,
            'energy_import': imports,
            'energy_export': exports,
            'energy_stored': storeds
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
