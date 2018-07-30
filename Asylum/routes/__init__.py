from . import energy
from . import auth
from . import blinds
from . import home
from . import locks


def init_routes(app):
    energy.init_energy_routes(app)
    blinds.init_blinds_routes(app)
    home.init_home_routes(app)
    locks.init_auth_routes(app)
