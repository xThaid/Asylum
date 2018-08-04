from flask import render_template
from Asylum.db_models.user import authorize


def init_home_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    @authorize
    def home(context):
        model = {
            'pageName': 'Strona Główna'
        }
        return render_template('home.html', model=model)
