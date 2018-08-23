from flask import render_template
from asylum.core.auth import authorize


def init_home_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def home(context):
        model = {
            'page_name': 'Strona Główna',
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                }]
        }
        return render_template('home.html', model=model)
