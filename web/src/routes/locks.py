from flask import render_template

from src.db_models.user import authorize


def init_auth_routes(app):
    @app.route('/locks', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def locks(context):
        model = {
            'page_name': 'Zamki',
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Zamki',
                    'href': '/locks'
                }
            ]
        }
        return render_template('locks.html', model=model)
