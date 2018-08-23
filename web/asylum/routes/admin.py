from flask import render_template

from asylum.core.auth import authorize


def init_auth_routes(app):
    @app.route('/admin', methods=['GET'])
    @authorize('admin')
    def admin(context):
        model = {
            'page_name': 'Panel Administracyjny',
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Panel administracyjny',
                    'href': '/admin'
                }
            ]
        }
        return render_template('admin.html', model=model)
