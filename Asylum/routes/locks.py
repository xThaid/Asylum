from flask import render_template

from Asylum.db_models.user import authorize


def init_auth_routes(app):
    @app.route('/locks', methods=['GET'])
    @authorize
    def locks(context):
        model = {
            'pageName': 'Zamki',
            'user': context['user']
        }
        return render_template('locks.html', model=model)
