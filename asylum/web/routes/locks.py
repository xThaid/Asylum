from flask import render_template

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize


def init_locks_routes(app):
    @app.route('/locks', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def locks(context):
        page_model = PageModel('Zamki', context['user'])\
            .add_breadcrumb_page('Zamki', '/locks')\
            .to_dict()
        return render_template('locks.html', page_model=page_model)
