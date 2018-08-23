import jwt
from flask import current_app, request, redirect, url_for
import datetime
from functools import wraps
from asylum.models.user import User
from asylum.models import db
import re


def register(username, name, password, repassword, role):
    if username is None \
       or name is None \
       or password is None \
       or repassword is None \
       or role is None:

        return {
            'response': {
                'status': 'error',
                'code': 3
                },
            'response_code': 400
        }
    if re.match('^[a-zA-Z0-9]{3,20}$', username) is None:
        return {
            'response': {
                'status': 'error',
                'code': 4
            },
            'response_code': 400
        }

    if re.match('^[a-zA-Z0-9]{3,20}$', name) is None:
        return {
            'response': {
                'status': 'error',
                'code': 5
            },
            'response_code': 400
        }

    if re.match('^(?=.*[A-Za-z])(?=.*\d)[\S]{8,}$', password) is None:
        return {
            'response': {
                'status': 'error',
                'code': 6
            },
            'response_code': 400
        }

    if repassword != password:
        return {
            'response': {
                'status': 'error',
                'code': 7
            },
            'response_code': 400
        }

    if role not in ['admin', 'user', 'guest']:
        return {
            'response': {
                'status': 'error',
                'code': 8
            },
            'response_code': 400
        }
    user = User(
        username=username,
        name=name,
        role=role
    ).hash_password(password)
    try:
        if not User.query.filter_by(username=username).first():
            db.session.add(user)
            db.session.commit()

            return {
                'response': {
                    'status': 'success',
                    'code': 0
                },
                'response_code': 201
            }
        else:
            return {
                'response': {
                    'status': 'error',
                    'code': 2
                },
                'response_code': 400
            }
    except Exception:
        return {
            'response': {
                'status': 'error',
                'code': 1
            },
            'response_code': 500
        }


def login(username, password):
    if username is None or password is None:
        return{
            'response': {
                'status': 'error',
                'code': 3
            },
            'response_code': 400
        }
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            token = encode_auth_token(user)
            return {
                'response':
                    {
                        'status': 'success',
                        'code': 0,
                        'url': url_for('home')
                    },
                'cookie': ['Authorization', 'Bearer ' + token.decode('utf-8')],
                'response_code': 200
            }
        else:
            return {
                'response':
                    {
                        'status': 'error',
                        'code': 2,
                    },
                'response_code': 401
            }
    except Exception:
        return {
            'response':
                {
                    'status': 'error',
                    'code': 1
                },
            'response_code': 500
        }


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
                return redirect(url_for('login'), code=302)

            data = request.cookies['Authorization']
            token = str.replace(str(data), 'Bearer ', '').encode('utf-8')
            try:
                context = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])['context']
            except:
                return redirect(url_for('login'), code=302)

            if context['user']['role'] not in roles:
                return redirect(url_for('login'), code=302)

            return f(context, *args, **kws)

        return decorated_function

    return decorator
