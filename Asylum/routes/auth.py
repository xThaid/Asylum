from flask import render_template, request, jsonify, make_response
from Asylum.db_models.user import User
import re


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
        return render_template('energy.html')

    @app.route('/auth/login', methods=['GET'])
    def login_page():
        return render_template('energy.html')

    @app.route('/auth/logout', methods=['POST'])
    def logout():
        return render_template('energy.html')
