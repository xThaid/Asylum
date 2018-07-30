from flask import render_template


def init_auth_routes(app):
    @app.route('/locks', methods=['GET'])
    def locks():
        model = {
            'pageName': 'Zamki'
        }
        return render_template('locks.html', model=model)
