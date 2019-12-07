from flask import jsonify, make_response
import datetime

from .api import bp, require_api_key, ok_request, msg_response

from asylum.asylumd import asylumd_client
from asylum.energy import energy_data
from asylum.web.models.energy import EnergyDaily, Energy
from asylum.web.routes.energy import MIN_DATE


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


@bp.route('/getHistoryEnergyData/<string:from_date>/<string:to_date>', methods=['GET', 'POST'])
@require_api_key
def get_history_energy_data(context, from_date, to_date):
    if from_date is None or to_date is None:
        return make_response('Missing params', 400)
    try:
        from_date_converted = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_converted = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
    except ValueError:
        return make_response('Wrong date format', 400)

    if from_date_converted > to_date_converted:
        return make_response('Wrong dates', 400)

    raw_data = EnergyDaily.get_last_rows(from_date_converted - datetime.timedelta(days=1), to_date_converted)

    if len(raw_data) == 0:
        return make_response('Wrong dates', 400)

        # Add data from current day
    if to_date_converted >= datetime.date.today():
        to_date_converted = datetime.date.today()
        current_day_first_entry = Energy.get_last_rows(
            datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(),
            datetime.datetime.now().timestamp(), 1)
        current_day_last_entry = Energy.get_last_rows(
            datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp(),
            datetime.datetime.now().timestamp(), 1, True)
        if len(current_day_first_entry) != 0:
            current_day_data = EnergyDaily()
            current_day_data.id = 0
            current_day_data.day_ordinal = datetime.date.today().toordinal()
            current_day_data.production = current_day_last_entry[0].production - current_day_first_entry[0].production
            current_day_data.import_ = current_day_last_entry[0].import_ - current_day_first_entry[0].import_
            current_day_data.export = current_day_last_entry[0].export - current_day_first_entry[0].export
            current_day_data.production_offset = current_day_last_entry[0].production
            current_day_data.import_offset = current_day_last_entry[0].import_
            current_day_data.export_offset = current_day_last_entry[0].export
            current_day_data.max_power_production = 0
            current_day_data.max_power_import = 0
            current_day_data.max_power_export = 0
            current_day_data.max_power_consumption = 0
            current_day_data.max_power_use = 0
            current_day_data.max_power_store = 0
            raw_data.append(current_day_data)

    # We have to make sure that very first day of measurements is also counted
    if MIN_DATE >= from_date_converted:
        from_date_converted = MIN_DATE
        dummy_day_data = EnergyDaily()
        dummy_day_data.day_ordinal = raw_data[0].day_ordinal - 1
        dummy_day_data.production = 0
        dummy_day_data.import_ = 0
        dummy_day_data.export = 0
        dummy_day_data.production_offset = 0
        dummy_day_data.import_offset = 0
        dummy_day_data.export_offset = 0
        dummy_day_data.max_power_production = 0
        dummy_day_data.max_power_import = 0
        dummy_day_data.max_power_export = 0
        dummy_day_data.max_power_consumption = 0
        dummy_day_data.max_power_use = 0
        dummy_day_data.max_power_store = 0
        raw_data.insert(0, dummy_day_data)

    production = raw_data[-1].production_offset - raw_data[0].production_offset
    import_ = raw_data[-1].import_offset - raw_data[0].import_offset
    export = raw_data[-1].export_offset - raw_data[0].export_offset
    use = production - export
    consumption = import_ + use
    store = export * 0.8 - import_

    production = round(production / 1000, 2)
    import_ = round(import_ / 1000, 2)
    export = round(export / 1000, 2)
    use = round(use / 1000, 2)
    consumption = round(consumption / 1000, 2)
    store = round(store / 1000, 2)

    return make_response(jsonify({
        'production': production,
        'consumption': consumption,
        'use': use,
        'import': import_,
        'export': export,
        'store': store
    }), 200)

