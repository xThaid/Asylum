from flask import render_template

from asylum.core.page_model import PageModel
from asylum.core.auth import authorize
from asylum.core import energy_data


def init_auth_routes(app):
    @app.route('/admin', methods=['GET'])
    @authorize('admin')
    def admin(context):
        page_model = PageModel('Panel Administracyjny', context['user'])\
            .add_breadcrumb_page('Panel Administracyjny', '/admin')\
            .to_dict()
        return render_template('admin.html', page_model=page_model)

    @app.route('/admin/status', methods=['GET'])
    @authorize('admin')
    def status(context):
        page_model = PageModel('Status urządzeń', context['user'])\
            .add_breadcrumb_page('Status urządzeń', '/admin/status')\
            .to_dict()
        data_model = {
            'flara_status': energy_data.test_flara_connection(),
            'emeter_status': energy_data.test_emeter_connection()
        }
        return render_template('admin/status.html', data_model=data_model, page_model=page_model)
