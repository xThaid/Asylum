from . import energy
from . import auth
from . import blinds
from . import home
from . import locks
from . import admin
from . import users
from . import meteo


def init_routes(app):
    energy.init_energy_routes(app)
    blinds.init_blinds_routes(app)
    home.init_home_routes(app)
    locks.init_locks_routes(app)
    auth.init_auth_routes(app)
    admin.init_auth_routes(app)
    users.init_users_routes(app)
    meteo.init_meteo_routes(app)
