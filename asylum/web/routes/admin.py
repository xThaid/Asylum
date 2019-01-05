from flask import render_template, jsonify
import requests

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize
from asylum.energy import energy_data
from asylum.meteo import meteo_data
from asylum import config


def init_auth_routes(app):
    @app.route('/admin', methods=['GET'])
    @authorize('admin')
    def admin(context):
        page_model = PageModel('Panel Administracyjny', context['user'])\
            .add_breadcrumb_page('Panel Administracyjny', '/admin')\
            .to_dict()
        return render_template('admin/admin.html', page_model=page_model)

    @app.route('/admin/status', methods=['GET'])
    @authorize('admin')
    def status(context):
        page_model = PageModel('Status urządzeń', context['user'])\
            .add_breadcrumb_page('Status urządzeń', '/admin/status')\
            .to_dict()
        data_model = {
            'flara_status': energy_data.test_flara_connection(),
            'emeter_status': energy_data.test_emeter_connection(),
            'meteo_status': meteo_data.test_meteo_connection()
        }
        return render_template('admin/status.html', data_model=data_model, page_model=page_model)

    @app.route('/admin/status/meteo', methods=['GET'])
    @authorize('admin')
    def status_meteo(context):
        return jsonify(requests.get(config['SUBSYSTEMS']['meteo_url'], timeout=3).json())

    @app.route('/admin/status/emeter', methods=['GET'])
    @authorize('admin')
    def status_emeter(context):
        return jsonify(requests.get(config['SUBSYSTEMS']['emeter_url'], timeout=3).json())
