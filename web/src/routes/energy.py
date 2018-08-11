from flask import render_template
from src.models.energy import EnergyIndexModel
from src.db_models.user import authorize


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def energy(context):
        return render_template('energy.html', model=vars(EnergyIndexModel(context)))
