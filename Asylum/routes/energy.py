from flask import render_template
import json
import datetime
import Asylum.models.energy as energy_model


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    def energy():
        power_production = energy_model.EnergyProduction.query.order_by(energy_model.EnergyProduction.id.desc())\
            .limit(1440).from_self().order_by(energy_model.EnergyProduction.id).all()
        energy_production = energy_model.EnergyProduction.query.order_by(energy_model.EnergyProduction.id.desc())\
            .limit(11520).from_self().order_by(energy_model.EnergyProduction.id).all()
        time = [datetime.datetime.fromtimestamp(o.time).strftime('%H:%M') for o in power_production]
        power = [o.power for o in power_production]
        energy_prod = [o.energy for o in energy_production][1::1440]
        energy_prod = [(y - x) / 1000 for x, y in zip(energy_prod, energy_prod[1:])]

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
            'energy': energy_prod,
            'maxPower': max(power)
        }
        return render_template('energy.html', model=model)
