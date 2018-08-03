from flask import render_template
from Asylum.models.energy import EnergyIndexModel


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    def energy():
        return render_template('energy.html', model=vars(EnergyIndexModel()))
