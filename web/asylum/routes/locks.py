from flask import render_template

from asylum.core.page_model import PageModel
from asylum.core.auth import authorize


def init_auth_routes(app):
    @app.route('/locks', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def locks(context):
        page_model = PageModel('Zamki', context['user'])\
            .add_breadcrumb_page('Zamki', '/locks')\
            .to_dict()
        return render_template('locks.html', page_model=page_model)
