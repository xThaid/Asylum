from functools import wraps

from flask import Blueprint, jsonify, make_response, request

from asylum.web.models.user import User

bp = Blueprint('api', __name__, url_prefix='/api')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        HEADER_KEY = 'X-API-KEY'

        if HEADER_KEY not in request.headers:
            return auth_fail()

        api_key = request.headers[HEADER_KEY]
        user = User.query.filter(User.api_key == api_key).first()
        if not user:
            return auth_fail()

        context = {
            'id': user.id,
            'name': user.name,
            'role': user.role
        }

        return f(context, *args, **kwargs)
    return decorated_function

def msg_response(msg, code):
    return make_response(jsonify(
        {
            'msg': msg
        }
    ), code)

def ok_request():
    return msg_response("success", 200)

def auth_fail():
    return msg_response("authorization failed", 401)


from . import methods