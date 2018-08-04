from flask import render_template, request, jsonify, make_response, redirect, url_for, current_app
from Asylum.db_models.user import User, authorize
import re
import jwt


def init_auth_routes(app):

    @app.route('/auth/register', methods=['POST'])
    def register():
        post_data = request.get_json()
        if post_data is None\
                or 'username' not in post_data\
                or 'name' not in post_data\
                or 'password' not in post_data\
                or 'repassword' not in post_data \
                or 'role' not in post_data \
                or post_data['username'] is None\
                or post_data['name'] is None\
                or post_data['password'] is None\
                or post_data['repassword'] is None\
                or post_data['role'] is None:
            response = {
                'status': 'error',
                'code': 3
            }
            return make_response(jsonify(response)), 400

        if re.match('^[a-zA-Z0-9]{3,20}$', post_data['username']) is None:
            response = {
                'status': 'error',
                'code': 4
            }
            return make_response(jsonify(response)), 400

        if re.match('^[a-zA-Z0-9]{3,20}$', post_data['name']) is None:
            response = {
                'status': 'error',
                'code': 5
            }
            return make_response(jsonify(response)), 400

        if re.match('^(?=.*[A-Za-z])(?=.*\d)[\S]{8,}$', post_data['password']) is None:
            response = {
                'status': 'error',
                'code': 6
            }
            return make_response(jsonify(response)), 400

        if post_data['repassword'] != post_data['password']:
            response = {
                'status': 'error',
                'code': 7
            }
            return make_response(jsonify(response)), 400

        if post_data['role'] not in ['admin', 'user', 'guest']:
            response = {
                'status': 'error',
                'code': 8
            }
            return make_response(jsonify(response)), 400

        user = User(
            username=post_data['username'],
            name=post_data['name'],
            role=post_data['role']
        )
        response = user\
            .hash_password(post_data['password'])\
            .register()

        if response['status'] == 'success':
            return make_response(jsonify(response)), 202

        return make_response(jsonify(response)), 400

    @app.route('/auth/register', methods=['GET'])
    def register_page():
        model = {
            'page_name': 'Tworzenie konta'
        }
        return render_template('auth/register.html', model=model)

    @app.route('/auth/login', methods=['POST'])
    def login():
        post_data = request.get_json()
        if post_data is None \
                or 'username' not in post_data \
                or 'password' not in post_data \
                or post_data['username'] is None \
                or post_data['password'] is None:
            response = {
                'status': 'error',
                'code': 3
            }
            return make_response(jsonify(response)), 400

        login_status = User.login(post_data)

        if login_status['response']['status'] == 'success':
            res = make_response(jsonify(login_status['response']))
            res.set_cookie(*login_status['cookie'], secure=False, httponly=True, samesite='strict')
            return res, 200

        return make_response(jsonify(login_status['response'])), 400

    @app.route('/auth/login', methods=['GET'])
    def login_page():
        if 'Authorization' not in request.cookies:
            return render_template('auth/login.html')

        context = None
        data = request.cookies['Authorization']
        token = str.replace(str(data), 'Bearer ', '').encode('utf-8')
        try:
            context = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])['context']
        except:
            return render_template('auth/login.html')

        return redirect(url_for('home'), code=302)

    @app.route('/auth/logout', methods=['POST'])
    @authorize
    def logout(context):
        return make_response(jsonify(context)), 200
