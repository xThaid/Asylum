from flask import Flask, url_for
from asylum.models import db
from . import config

app = Flask(__name__, static_folder='../static')
with app.app_context():
    app.config.from_object(config.Config)
    db.init_app(app)
    from . import routes
    routes.init_routes(app)

