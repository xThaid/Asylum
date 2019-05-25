from flask import Flask

from asylum import config
from asylum.web import routes
from asylum.web.api import api
from asylum.web.models import db


class AppConfig(object):
    SECRET_KEY = config['SECURITY']['SecretKey']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + config['DATABASE']['Path']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__, static_folder='static')
app.config.from_object(AppConfig)
db.init_app(app)
routes.init_routes(app)

app.register_blueprint(api.bp)
