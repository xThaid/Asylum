from flask import render_template, request, current_app
import jwt

from asylum.core import auth, web_response
from asylum.core.page_model import PageModel
from asylum.core.auth import authorize


def init_auth_routes(app):

    @app.route('/auth/register', methods=['POST'])
    @authorize('admin', 'none')
    def register(context):
        post_data = request.get_json()
        if post_data is None\
                or 'username' not in post_data\
                or 'name' not in post_data\
                or 'password' not in post_data\
                or 'repassword' not in post_data \
                or 'role' not in post_data:

            return web_response.bad_request()

        return auth.register(post_data['username'],
                             post_data['name'],
                             post_data['password'],
                             post_data['repassword'],
                             post_data['role'])

    @app.route('/auth/register', methods=['GET'])
    @authorize('admin', 'none')
    def register_page(context):
        page_model = PageModel('Tworzenie konta', context['user'])\
            .add_breadcrumb_page('Panel Administracyjny', '/admin')\
            .add_breadcrumb_page('Rejestracja', '/auth/register')\
            .to_dict()
        return render_template('auth/register.html', page_model=page_model)

    @app.route('/auth/login', methods=['POST'])
    def login():
        post_data = request.get_json()
        if post_data is None \
                or 'username' not in post_data \
                or 'password' not in post_data:
            return web_response.bad_request()

        return auth.login(post_data['username'], post_data['password'])

    @app.route('/auth/login', methods=['GET'])
    def login_page():
        if 'Authorization' not in request.cookies:
            return render_template('auth/login.html')

        data = request.cookies['Authorization']
        token = str.replace(str(data), 'Bearer ', '').encode('utf-8')
        try:
            jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])['context']
        except:
            return render_template('auth/login.html')

        return web_response.redirect_to('home')

    @app.route('/auth/logout', methods=['GET'])
    def logout():
        return web_response.logout()
