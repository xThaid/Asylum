from flask import render_template

from Asylum.db_models.user import authorize


def init_blinds_routes(app):
    @app.route('/blinds', methods=['GET'])
    @authorize
    def blinds(context):
        model = {
            'pageName': 'Rolety',
            'user': context['user']
        }
        return render_template('blinds.html', model=model)
