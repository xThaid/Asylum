from flask import render_template


def init_home_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    def home():
        model = {
            'pageName': 'Strona Główna'
        }
        return render_template('home.html', model=model)
