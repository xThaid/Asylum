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

    #asylumd_client.gateAction(gate_id)

    return ok_request()

@bp.route('/shutterOpen/<int:shutter_id>', methods=['GET', 'POST'])
@require_api_key
def shutter_open(context, shutter_id):
    if shutter_id < 0 or shutter_id > 8:
        return msg_response("wrong shutter id", 400)

    #asylumd_client.shutterAction(shutter_id, 0)
    return ok_request()

@bp.route('/shutterClose/<int:shutter_id>', methods=['GET', 'POST'])
@require_api_key
def shutter_close(context, shutter_id):
    if shutter_id < 0 or shutter_id > 8:
        return msg_response("wrong shutter id", 400)

    #asylumd_client.shutterAction(shutter_id, 1)
    return ok_request()

@bp.route('/shutterStop/<int:shutter_id>', methods=['GET', 'POST'])
@require_api_key
def shutter_stop(context, shutter_id):
    if shutter_id < 0 or shutter_id > 8:
        return msg_response("wrong shutter id", 400)

    #asylumd_client.shutterAction(shutter_id, 2)
    return ok_request()


