from flask import render_template
from flask import jsonify
import requests
import json
import datetime
from . import models


def init_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    def home():
        model = {
            'pageName': 'Strona Główna'
        }
        return render_template('home.html', model=model)

    @app.route('/energy', methods=['GET'])
    def energy():
        power_production = models.EnergyProduction.query.order_by(models.EnergyProduction.id.desc()).limit(1440)\
            .from_self().order_by(models.EnergyProduction.id).all()
        energy_production = models.EnergyProduction.query.order_by(models.EnergyProduction.id.desc()).limit(11520) \
            .from_self().order_by(models.EnergyProduction.id).all()
        time = [datetime.datetime.fromtimestamp(o.time).strftime('%H:%M') for o in power_production]
        power = [o.power for o in power_production]
        energy = [o.energy for o in energy_production][1::1440]
        energy = [(y - x)/1000 for x, y in zip(energy, energy[1:])]

        print(energy)
        model = {
            'pageName': 'Energia',
            'chartData': json.dumps(
                {
                    'labels': time[1::5],
                    'datasets':
                        [{
                            'label': 'Test',
                            'data': power[1::5],
                            'borderWidth': 1,
                            'backgroundColor': 'rgba(40, 255, 70, 0.5)'
                        }]
                }
            ),
            'currentPower': power[-1],
            'energy': energy,
            'maxPower': max(power)
        }
        return render_template('energy.html', model=model)

    @app.route('/blinds', methods=['GET'])
    def blinds():
        model = {
            'pageName': 'Rolety'
        }
        return render_template('blinds.html', model=model)

    @app.route('/locks', methods=['GET'])
    def locks():
        model = {
            'pageName': 'Zamki'
        }
        return render_template('locks.html', model=model)
