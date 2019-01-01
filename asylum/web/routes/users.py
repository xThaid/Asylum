from flask import render_template, request

from asylum.web.core import validate_json, web_response
from asylum.web.core.page_model import PageModel
from asylum.web.core.auth import authorize

from asylum.web.models import db
from asylum.web.models.user import MacAddress


def init_users_routes(app):

    @app.route('/users', methods=['GET'], defaults={'user_id': None})
    @app.route('/users/<int:user_id>', methods=['GET'])
    @authorize('user', 'admin')
    def mac_address(context, user_id):
        if user_id is None:
            user_id = context['user']['id']

        query_result = MacAddress\
            .query \
            .filter(MacAddress.user_id == user_id)\
            .all()

        mac_addresses = [{
            'id': x.id,
            'address': x.mac_address
        } for x in query_result]

        page_model = PageModel('Adresy MAC', context['user'])\
            .add_breadcrumb_page('Adresy MAC', '')\
            .to_dict()

        return render_template('users.html',
                                data_model=mac_addresses,
                                page_model=page_model)

    @app.route('/users/addMacAddress', methods=['POST'], defaults={'user_id': None})
    @app.route('/users/<int:user_id>/addMacAddress', methods=['POST'])
    @authorize('user', 'admin')
    def add_mac_address(context, user_id):
        if user_id is None:
            user_id = context['user']['id']

        json = request.get_json()

        if not validate_json.validate(validate_json.add_mac_address_schema, json):
            return web_response.bad_request()

        try:
            db.session.add(MacAddress(
                user_id=user_id,
                mac_address=json['mac_address'].lower()
            ))
            db.session.commit()
        except:
            return web_response.database_error()

        return web_response.ok_request()

    @app.route('/users/deleteMacAddress', methods=['POST'], defaults={'user_id': None})
    @app.route('/users/<int:user_id>/deleteMacAddress', methods=['POST'])
    @authorize('user', 'admin')
    def delete_mac_address(context, user_id):
        if user_id is None:
            user_id = context['user']['id']

        json = request.get_json()
        if not validate_json.validate(validate_json.delete_mac_address_schema, json):
            return web_response.bad_request()

        try:
            MacAddress.query.filter_by(id=json['mac_address_id']).delete()
            db.session.commit()
        except:
            return web_response.database_error()

        return web_response.ok_request()
