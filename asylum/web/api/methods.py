from flask import jsonify, make_response, request
import datetime

from .api import bp, require_api_key, ok_request, msg_response

from asylum.asylumd import asylumd_client
from asylum.energy import energy_data
from asylum.web.core import data_grouper


@bp.route('/ping', methods=['GET', 'POST'])
def ping():
    return msg_response("pong", 200)


@bp.route('/getUserInfo', methods=['GET', 'POST'])
@require_api_key
def check_login(context):
    return make_response(jsonify({
        'id': context['id'],
        'name': context['name'],
        'role': context['role']}), 200)


@bp.route('/gateOpen', methods=['POST'])
@require_api_key
def gate_open(context):
    if gate_controller.open_gate() == True:
        return ok_request()

    return msg_response("gate controller is not responding", 500)


@bp.route('/blindAction/<int:blind_id>/<int:action_id>', methods=['GET', 'POST'])
@require_api_key
def blind_action(context, blind_id, action_id):
    if blind_id < 0 or blind_id > 8:
        return msg_response("wrong shutter id", 400)

    if action_id < 0 or action_id > 2:
        return msg_response("wrong action id", 400)

    asylumd_client.shutterAction(blind_id, action_id)
    return ok_request()


@bp.route('/blindAction/all/<int:action_id>', methods=['GET', 'POST'])
@require_api_key
def blind_action_all(context, action_id):
    if action_id < 0 or action_id > 2:
        return msg_response("wrong action id", 400)
    for x in range(9):
        asylumd_client.shutterAction(x, action_id)
    return ok_request()


@bp.route('/getCurrentPowerData', methods=['GET', 'POST'])
@require_api_key
def get_power_data(context):
    current_data = energy_data.get_data()

    if current_data is None:
        return make_response('Urządzenia pomiarowe nie odpowiadają', 500)

    return make_response(jsonify({
        'production': current_data['power_production'],
        'consumption': current_data['power_consumption'],
        'use': current_data['power_use'],
        'import': current_data['power_import'],
        'export': current_data['power_export'],
        'store': current_data['power_store']
    }), 200)


@bp.route('/getHistoryEnergyData', methods=['POST'])
@require_api_key
def get_history_energy_data(context):
    post_data = request.get_json()
    if post_data is None:
        return make_response('Missing params - ERR1', 400)

    if 'from_date' not in post_data or 'to_date' not in post_data or 'group_span' not in post_data:
        return make_response('Missing params - ERR2', 400)

    post_from_date = post_data['from_date']
    post_to_date = post_data['to_date']
    post_group_span = post_data['group_span']

    if post_from_date is None or post_to_date is None or post_group_span is None:
        return make_response('Missing params - ERR3', 400)

    if post_group_span not in data_grouper.GROUP_SPANS:
        return make_response('Wrong group_span', 400)
    try:
        from_date = datetime.datetime.strptime(post_from_date, '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(post_to_date, '%Y-%m-%d').date()
    except ValueError:
        return make_response('Wrong date format', 400)

    data = data_grouper.aggregate_energy_data(from_date, to_date, post_group_span)

    if data is None:
        return make_response('Error during grouping data', 400)

    return make_response(jsonify(data), 200)

