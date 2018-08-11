from flask import render_template

from src.db_models.user import authorize


def init_blinds_routes(app):
    @app.route('/blinds', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def blinds(context):
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
        return render_template('blinds.html', model=model)
