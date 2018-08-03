from . import db
from passlib.hash import pbkdf2_sha256
import jwt
from flask import current_app
import datetime


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
        user = User.query.filter_by(username=self.username).first()
        if not user:
            try:
                db.session.add(self)
                db.session.commit()

                return {
                    'status': 'success',
                    'code': 0
                }
            except Exception:
                return {
                    'status': 'error',
                    'code': 1
                }
        else:
            return {
                'status': 'warning',
                'code': 2
            }

    def encode_auth_token(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired'
        except jwt.InvalidTokenError:
            return 'Invalid token'

    def __repr__(self):
        return '<User :{}>'.format(self.username)
