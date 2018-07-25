from flask import render_template
from flask import jsonify
import requests
from . import models


def init_routes(app):

    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    def home():
        model={
            'pageName': 'Strona Główna'
        }
        return render_template('home.html', model=model)

    @app.route('/energy', methods=['GET'])
    def energy():
        powerProduction = models.EnergyProduction.query.order_by(models.EnergyProduction.id.desc()).first();
        model={
            'pageName': 'Energia'
        }
        return render_template('energy.html', model=model)

    @app.route('/blinds', methods=['GET'])
    def blinds():
        model={
            'pageName': 'Rolety'
        }
        return render_template('blinds.html', model=model)

    @app.route('/locks', methods=['GET'])
    def locks():
        model={
            'pageName': 'Zamki'
        }
        return render_template('locks.html', model=model)
