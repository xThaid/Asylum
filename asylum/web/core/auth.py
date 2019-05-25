import jwt
import datetime
import secrets
from functools import wraps

from flask import current_app, request
from sqlalchemy import func

from asylum.helpers import get_MAC_address
from asylum.web.core import web_response

from asylum.web.models import db
from asylum.web.models.user import User, MacAddress

def gen_api_key():
    return secrets.token_hex(16)

def register(username, name, password, role):
    try:
        if not User.query.filter_by(username=username).first():
            api_key = gen_api_key()
            db.session.add(User(
                username=username,
                name=name,
                role=role,
                api_key=api_key
            ).hash_password(password))

            db.session.commit()

            return web_response.user_added()
        else:
            return web_response.user_already_exist()
    except Exception:
        return web_response.database_error()


def login(username, password):
    try:
        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        if user and user.verify_password(password):
            token = encode_auth_token(user)
            return web_response.login_success(['Authorization', 'Bearer ' + token.decode('utf-8')])
        else:
            return web_response.login_failed()
    except Exception:
        return web_response.database_error()


def try_to_autologin(ip_address):
    addr = get_MAC_address(ip_address)
    if addr is None:
        return None
    mac_address = MacAddress.query.filter(func.lower(MacAddress.mac_address) == func.lower(addr)).first()
    if not mac_address:
        return None

    token = encode_auth_token(mac_address.user)
    return web_response.auto_login(['Authorization', 'Bearer ' + token.decode('utf-8')])


def encode_auth_token(user):
    payload = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10),
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


def unauthorize(f):
    @wraps(f)
    def decorator(*args, **kws):
        if 'Authorization' not in request.cookies:
            return f(*args, **kws)

        data = request.cookies['Authorization']
        token = str.replace(str(data), 'Bearer ', '').encode('utf-8')

        try:
            jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])['context']
        except:
            return f(*args, **kws)

        return web_response.redirect_to('home')
    return decorator


def authorize(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kws):
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
