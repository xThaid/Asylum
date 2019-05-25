from flask import render_template

from asylum.asylumd import asylumd_client

from asylum.web.core import web_response

from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize


def init_home_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def home(context):
        page_model = PageModel('Strona Główna', context['user'])\
            .to_dict()
        return render_template('home.html', page_model=page_model)


    @app.route('/gateOpen', methods=['POST'])
    @authorize('user', 'admin')
    def gate_open(context):
        # asylumd_client.gateAction(0)
        
        return web_response.ok_request()