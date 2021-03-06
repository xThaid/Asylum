from flask import render_template, request

from asylum.web.core import auth, web_response
from asylum.web.core import validate_json
from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize, unauthorize


def init_auth_routes(app):
    @app.route('/auth/register', methods=['POST'])
    @authorize('admin')
    def register(context):
        json = request.get_json()

        if not validate_json.validate_register(json):
            return web_response.bad_request()

        return auth.register(json['login'],
                             json['name'],
                             json['password'],
                             json['role'])

    @app.route('/auth/register', methods=['GET'])
    @authorize('admin')
    def register_page(context):
        page_model = PageModel('Tworzenie konta', context['user'])\
            .add_breadcrumb_page('Panel Administracyjny', '/admin')\
            .add_breadcrumb_page('Rejestracja', '/auth/register')\
            .to_dict()
        return render_template('auth/register.html', page_model=page_model)

    @app.route('/auth/login', methods=['POST'])
    @unauthorize
    def login():
        json = request.get_json()

        if not validate_json.validate(validate_json.login_schema, json):
            return web_response.bad_request()

        return auth.login(json['login'], json['password'])

    @app.route('/auth/login', methods=['GET'])
    @unauthorize
    def login_page():
        resp = auth.try_to_autologin(request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else None
        if resp is not None:
            return resp

        return render_template('auth/login.html')

    @app.route('/auth/logout', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def logout(context):
        return web_response.logout()
