import jwt
from flask import current_app, request
import datetime
from functools import wraps
import re

from asylum.core import web_response
from asylum.models import db
from asylum.models.user import User


def register(username, name, password, repassword, role):

    if username is None \
       or name is None \
       or password is None \
       or repassword is None \
       or role is None\
       or re.match('^[a-zA-Z0-9]{3,20}$', username) is None\
       or re.match('^[a-zA-Z0-9]{3,20}$', name) is None\
       or re.match('^(?=.*[A-Za-z])(?=.*\d)[\S]{8,}$', password) is None\
       or repassword != password \
       or role not in ['admin', 'user', 'guest']:

        return web_response.bad_request()

    user = User(
        username=username,
        name=name,
        role=role
    ).hash_password(password)
    try:
        if not User.query.filter_by(username=username).first():
            db.session.add(user)
            db.session.commit()

            return web_response.user_added()
        else:
            return web_response.user_already_exist()
    except Exception:
        return web_response.database_error()


def login(username, password):
    if username is None or password is None:
        return web_response.login_failed()
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            token = encode_auth_token(user)
            return web_response.login_success(['Authorization', 'Bearer ' + token.decode('utf-8')])
        else:
            return web_response.login_failed()
    except Exception:
        return web_response.database_error()


def encode_auth_token(user):
    payload = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'sub': user.id,
        "context": {
            "user": {
                'id': user.id,
                'name': user.name,
                'role': user.role
            }
        }
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        'HS256'
    )


def authorize(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kws):
            if 'none' in roles:
                context = {
                    "user": {
                        'id': -1,
                        'name': 'none',
                        'role': 'none'
                    }}
                return f(context, *args, **kws)
            if 'Authorization' not in request.cookies:
                return web_response.redirect_to('login')

            data = request.cookies['Authorization']
            token = str.replace(str(data), 'Bearer ', '').encode('utf-8')
            try:
                context = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])['context']
            except:
                return web_response.redirect_to('login')

            if context['user']['role'] not in roles:
                return web_response.redirect_to('login')

            return f(context, *args, **kws)

        return decorated_function

    return decorator
