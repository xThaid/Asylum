from flask import render_template
from Asylum.models.energy import EnergyIndexModel
from Asylum.db_models.user import authorize


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    @authorize
    def energy(context):
        return render_template('energy.html', model=vars(EnergyIndexModel(context)))
