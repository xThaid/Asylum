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

    @app.route('/energy/getCurrentPowerData', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def get_current_power_data(context):
        current_data = energy_data.get_data()

        return jsonify({
            'production': current_data['power_production'],
            'consumption': current_data['power_consumption'],
            'use': current_data['power_use'],
            'import': current_data['power_import'],
            'export': current_data['power_export'],
            'store': current_data['power_store']
            })
