from flask import render_template

from asylum.asylumd import asylumd_client

from asylum.web.core import web_response

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize

import asylum.web.routes.energy as energy
from asylum.web.models.energy import EnergyCorrection

import datetime

def init_home_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def home(context):
        page_model = PageModel('Strona Główna', context['user'])\
            .to_dict()

        _, energy_total_daily, _, _ = energy.aggregate_energy_daily_data(datetime.datetime.combine(datetime.date.today(), datetime.time()))

        aggregated = energy.aggregate_energy_data(energy.MIN_DATE, 'all')

        correction = EnergyCorrection.get_total_correction()[0] / 1000.0

        data_model = {
            'energy': {
                'daily_prod': energy_total_daily['production'],
                'daily_cons': energy_total_daily['consumption'],
                'total_balance': aggregated['energy_total']['store'] + correction
            }
        }

        return render_template('home.html', page_model=page_model, data_model=data_model)


    @app.route('/gateOpen', methods=['POST'])
    @authorize('user', 'admin')
    def gate_open(context):
        # asylumd_client.gateAction(0)
        
        return web_response.ok_request()