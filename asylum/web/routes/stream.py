from flask import render_template, jsonify
import requests

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize
from asylum.energy import energy_data
from asylum.meteo import meteo_data
from asylum import config


def init_stream_routes(app):
    @app.route('/streams/<string:stream_id>', methods=['GET'])
    @authorize('user', 'admin')
    def stream(context, stream_id):
        resp = requests.get('http://localhost:8002/streams').json()
        url = ""
        for x in resp:
            if x['id'] == stream_id:
                url = x['url']
        print(url)

        data_model = {
            'url': "https://asylum.zapto.org" + url
        }
        page_model = PageModel('Strumienie', context['user'])\
            .add_breadcrumb_page('Strumienie', '/stream')\
            .to_dict()
        return render_template('stream.html', data_model=data_model, page_model=page_model)