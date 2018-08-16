from . import db
from passlib.hash import pbkdf2_sha256
import jwt
from flask import current_app, abort, request, redirect, url_for
import datetime
from functools import wraps


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)

    def hash_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)
        return self

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def register(self):
        try:
            user = User.query.filter_by(username=self.username).first()
            if not user:
                    db.session.add(self)
                    db.session.commit()

                    return {
                        'status': 'success',
                        'code': 0
                    }
            else:
                return {
                    'status': 'error',
                    'code': 2
                }
        except Exception:
            return {
                'status': 'error',
                'code': 1
            }

    @staticmethod
    def login(data):
        try:
            user = User.query.filter_by(username=data['username']).first()
            if user and user.verify_password(data['password']):
                token = user.encode_auth_token()
                return {
                    'response':
                    {
                        'status': 'success',
                        'code': 0,
                        'url': url_for('home')
                    },
                    'cookie': ['Authorization', 'Bearer ' + token.decode('utf-8')]
                }
            else:
                return {
                    'response':
                    {
                        'status': 'error',
                        'code': 2,
                    },
                }
        except Exception:
            return {
                    'response':
                    {
                        'status': 'error',
                        'code': 1
                    },
                }

    def encode_auth_token(self):
        payload = {
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'sub': self.id,
            "context": {
                "user": {
                    'id': self.id,
                    'name': self.name,
                    'role': self.role
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
                    'name': 'unauthorized',
                    'role': 'unauthorized'
                }}
                return f(context, *args, **kws)
            if 'Authorization' not in request.cookies:
                return redirect(url_for('login'), code=302)

            context = None
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
