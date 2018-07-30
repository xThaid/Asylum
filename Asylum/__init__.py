from flask import Flask
from Asylum.models import db
from . import config

app = Flask(__name__)

app.config.from_object(config.Config)
db.init_app(app)
from . import routes
routes.init_routes(app)
