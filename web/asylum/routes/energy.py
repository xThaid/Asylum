from flask import render_template, jsonify

from asylum.core.page_model import PageModel
from asylum.core.auth import authorize
from asylum.core import energy_data


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def energy(context):
        page_model = PageModel('Energia', context['user'])\
            .add_breadcrumb_page('Energia', '/energy')\
            .to_dict()

        return render_template('energy.html', page_model=page_model)

    @app.route('/energy/getCurrentData', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def get_current_energy_data(context):
        current_data = energy_data.get_data()
        current_energy_data = {
            'production':
                {
                    'current': current_data['power_production'],
                    'max': 1000,
                    'average': 1000,
                    'energy': 12.12
                },
            'consumption':
                {
                    'current': 1000,
                    'max': 1000,
                    'average': 1000,
                    'energy': 12.12
                },
            'summary':
                {
                    'power_use': 1000,
                    'power_import': 1000,
                    'power_export': 1000,
                    'power_store': 1000,
                    'energy_use': 11.11,
                    'energy_import': 11.11,
                    'energy_export': 11.11,
                    'energy_store': 11.11,
                }
            }
        return jsonify(current_energy_data)
