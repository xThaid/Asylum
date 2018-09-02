from flask import render_template

from asylum.core.page_model import PageModel
from asylum.core.auth import authorize


def init_auth_routes(app):
    @app.route('/admin', methods=['GET'])
    @authorize('admin')
    def admin(context):
        page_model = PageModel('Panel Administracyjny', context['user'])\
            .add_breadcrumb_page('Panel Administracyjny', '/admin')\
            .to_dict()
        return render_template('admin.html', page_model=page_model)
