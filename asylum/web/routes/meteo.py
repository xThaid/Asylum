from flask import render_template, make_response, jsonify

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize
from asylum.meteo import meteo_data


def init_meteo_routes(app):
    @app.route('/meteo', methods=['GET'])
    @app.route('/meteo/', methods=['GET'])
    @app.route('/meteo/now', methods=['GET'])
    @app.route('/meteo/now/', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def meteo_now(context):
        page_model = PageModel('Stacja meteo - strona główna', context['user'])\
            .add_breadcrumb_page('Stacja meteo', '/meteo')\
            .to_dict()
        return render_template('meteo/now.html', page_model=page_model)

    @app.route('/meteo/getCurrentData', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def get_current_meteo_data(context):
        current_data = meteo_data.get_data()

        if current_data is None:
            return make_response('', 500)

        return jsonify({
            'temperature': current_data['temperature'],
            'humidity': current_data['humidity'],
            'pressure': current_data['pressure'],
            'dust_PM10': current_data['dust_PM10'],
            'dust_PM25': current_data['dust_PM25'],
            'dust_PM100': current_data['dust_PM100']
        })
