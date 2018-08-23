from flask import render_template, request, jsonify, make_response, redirect, url_for, current_app
from asylum.core.auth import authorize
from asylum.core import auth
import jwt


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
            response = {
                'status': 'error',
                'code': 3
            }
            return make_response(jsonify(response)), 400

        response = auth.register(post_data['username'],
                                 post_data['name'],
                                 post_data['password'],
                                 post_data['repassword'],
                                 post_data['role'])

        return make_response(jsonify(response['response'])), response['response_code']

    @app.route('/auth/register', methods=['GET'])
    @authorize('admin', 'none')
    def register_page(context):
        model = {
            'page_name': 'Tworzenie konta',
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Panel administracyjny',
                    'href': '/admin'
                },
                {
                    'name': 'Rejestracja',
                    'href': '/auth/register'
                }
            ]
        }
        return render_template('auth/register.html', model=model)

    @app.route('/auth/login', methods=['POST'])
    def login():
        post_data = request.get_json()
        if post_data is None \
                or 'username' not in post_data \
                or 'password' not in post_data:
            response = {
                'status': 'error',
                'code': 3
            }
            return make_response(jsonify(response)), 400

        login_status = auth.login(post_data['username'], post_data['password'])

        if login_status['response']['code'] == 0:
            res = make_response(jsonify(login_status['response']))
            res.set_cookie(*login_status['cookie'], secure=False, httponly=True, samesite='strict')
            return res, login_status['response_code']

        return make_response(jsonify(login_status['response'])), login_status['response_code']

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

        return redirect(url_for('home'), code=302)

    @app.route('/auth/logout', methods=['GET'])
    def logout():
        res = make_response(redirect(url_for('login'), code=302))
        res.set_cookie('Authorization', '', expires=0, secure=False, httponly=True, samesite='strict')
        return res
