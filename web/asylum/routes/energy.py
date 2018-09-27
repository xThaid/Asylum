from flask import render_template, jsonify, make_response
from datetime import datetime, timedelta
import time

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

            productions.append(prod)
            imports.append(imp)
            exports.append(exp)

            consumptions.append(prod - exp + imp)
            uses.append(prod - exp)
            storeds.append(exp * 0.8 - imp)

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

        data_model = {
            'power_production_average': int(production_delta * 3600 / time_from_midnight),
            'power_production_max': 1,
            'energy_production': productions,
            'energy_production_total': production_delta / 1000,
            'power_consumption_average': int(consumption_delta * 3600 / time_from_midnight),
            'power_consumption_max': 1,
            'energy_consumption': consumptions,
            'energy_consumption_total': consumption_delta / 1000,
            'energy_use': uses,
            'energy_use_total': use_delta / 1000,
            'energy_import': imports,
            'energy_import_total': import_delta / 1000,
            'energy_export': exports,
            'energy_export_total': export_delta / 1000,
            'energy_stored': storeds,
            'energy_stored_total': stored_delta / 1000
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
