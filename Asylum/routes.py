from flask import render_template
from flask import jsonify
import requests
from . import models


def init_routes(app):

    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    def home():
        return render_template('home.html')

    @app.route('/getConsumption', methods=['GET'])
    def get_consumption():
        res = requests.get('http://192.168.1.102').json()
        return jsonify(res)

    @app.route('/energy', methods=['GET'])
    def energy():
        powerProduction = models.EnergyProduction.query.order_by(models.EnergyProduction.id.desc()).first();
        print(powerProduction)
        return render_template('energy.html')

    @app.route('/blinds', methods=['GET'])
    def blinds():
        return render_template('blinds.html')

    @app.route('/locks', methods=['GET'])
    def locks():
        return render_template('locks.html')
