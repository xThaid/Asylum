from . import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    api_key = db.Column(db.String(32), nullable=False)

    def hash_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)
        return self

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def __repr__(self):
        return ('User<id:%i ,username: %s, name: %s, role: %s' %
                (self.id, self.username, self.name, self.role)) + '>'


class MacAddress(db.Model):
    __tablename__ = 'user_mac_address'
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")

    def __repr__(self):
        return ('Mac Address<id:%i ,user id: %s, mac address: %s' %
                (self.id, self.user_id, self.mac_address)) + '>'