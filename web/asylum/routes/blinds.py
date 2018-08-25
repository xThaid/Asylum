from flask import render_template

from asylum.core.auth import authorize


def init_blinds_routes(app):
    @app.route('/blinds', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def index(context):
        model = {
            'page_name': 'Rolety',
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Rolety',
                    'href': '/blinds'
                }
            ]
        }
        return render_template('blinds/index.html', model=model)

    @app.route('/blinds/manage/<int:blind_id>', methods=['GET'])
    @authorize('user', 'admin')
    def manage(context, blind_id):
        model = {
            'page_name': 'Zarządzaj roletą nr ' + str(blind_id),
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Rolety',
                    'href': '/blinds'
                },
                {
                    'name': 'Zarządzanie roletą',
                    'href': '/blinds'
                }

            ]
        }
        return render_template('blinds/manage.html', model=model)