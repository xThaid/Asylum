from flask import render_template, jsonify
import requests

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize
from asylum.energy import energy_data
from asylum.meteo import meteo_data
from asylum import config


def init_stream_routes(app):

    @app.route('/streams', methods=['GET'])
    @authorize('user', 'admin')
    def streams(context):
        resp = requests.get('http://localhost:8002/streams').json()
        
        strs = [x['id'] for x in resp]

        data_model = {
            'streams': strs
        }
        page_model = PageModel('Kamery', context['user'])\
            .add_breadcrumb_page('Kamery', '/streams')\
            .to_dict()
        return render_template('streams.html', data_model=data_model, page_model=page_model)

    @app.route('/streams/<string:stream_id>', methods=['GET'])
    @authorize('user', 'admin')
    def stream(context, stream_id):
        resp = requests.get('http://localhost:8002/streams').json()
        url = ""
        for x in resp:
            if x['id'] == stream_id:
                url = x['url']

        data_model = {
            'url': "https://asylum.zapto.org" + url
        }
        page_model = PageModel('Kamery', context['user'])\
            .add_breadcrumb_page('Kamery', '/streams')\
            .to_dict()
        return render_template('stream.html', data_model=data_model, page_model=page_model)

    @app.route('/recording/<string:recording_id>/<string:date>/<string:hour>', methods=['GET'])
    @authorize('user', 'admin')
    def recording(context, recording_id, date, hour):
        resp = requests.get('http://192.168.1.100:8002/recordings/' + recording_id + '/' + date).json()
        url = ""
        for x in resp:
            if x['hour'] == hour:
                url = x['url']

        data_model = {
            'url': "https://asylum.zapto.org" + url
        }
        page_model = PageModel('Nagrania', context['user'])\
            .add_breadcrumb_page('Nagrania', '/recording')\
            .to_dict()
        return render_template('stream.html', data_model=data_model, page_model=page_model)