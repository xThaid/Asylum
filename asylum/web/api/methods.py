from flask import jsonify, make_response

from .api import bp, require_api_key, ok_request, msg_response

from asylum.asylumd import asylumd_client


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


@bp.route('/gateOpen/<int:gate_id>', methods=['GET', 'POST'])
@require_api_key
def gate_open(context, gate_id):
    if gate_id < 0 or gate_id > 3:
        return msg_response("wrong gate id", 400)

    asylumd_client.gateAction(gate_id)

    return ok_request()


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

