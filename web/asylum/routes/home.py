from flask import render_template

from asylum.core.page_model import PageModel
from asylum.core.auth import authorize


def init_home_routes(app):
    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def home(context):
        page_model = PageModel('Strona Główna', context['user'])\
            .to_dict()
        return render_template('home.html', page_model=page_model)
