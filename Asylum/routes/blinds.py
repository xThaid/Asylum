from flask import render_template


def init_blinds_routes(app):
    @app.route('/blinds', methods=['GET'])
    def blinds():
        model = {
            'pageName': 'Rolety'
        }
        return render_template('blinds.html', model=model)
