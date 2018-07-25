from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import config

app = Flask(__name__)

app.config.from_object(config.Config)
db = SQLAlchemy(app)
from . import routes
routes.init_routes(app)
