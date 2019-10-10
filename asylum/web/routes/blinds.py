from flask import render_template, request
from datetime import timedelta

from asylum.asylumd import asylumd_client

from asylum.web.core import web_response
from asylum.web.core import names
from asylum.web.core import validate_json
from asylum.web.core.utilities import unixtime_to_strftime
from asylum.web.core.auth import authorize
from asylum.web.core.page_model import PageModel

from asylum.web.models import db
from asylum.web.models.blinds import BlindsTask, BlindsSchedule
from asylum.web.models.user import User


def init_blinds_routes(app):

    @app.route('/blinds', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def blinds_index(context):
        page_model = PageModel('Rolety', context['user'])\
            .add_breadcrumb_page('Rolety', '/blinds')\
            .to_dict()

        data_model = {
            'devices_names': names.devices
        }
        return render_template('blinds/index.html', data_model=data_model, page_model=page_model)

    @app.route('/blinds/manage/<string:blinds_id>', methods=['GET'])
    @authorize('user', 'admin')
    def blinds_manage(context, blinds_id):
        blinds_id_list = list(
            map(lambda x: int(x), list(
                filter(lambda x: x.isdigit() and names.devices.get(int(x)), blinds_id.split(',')))
                )
        )

        if len(blinds_id_list) == 0:
            return web_response.redirect_to('blinds_index')

        task_query_result = BlindsTask\
            .query \
            .filter(BlindsTask.device.in_(blinds_id_list))\
            .join(User)\
            .add_column(User.name)\
            .all()
        
        scheduled_task_query_result = BlindsTask\
            .query \
            .filter(BlindsTask.device.in_(blinds_id_list))\
            .filter(BlindsTask.user_id == None)\
            .order_by(BlindsTask.time)\
            .all()

        tasks = []
        for x in task_query_result:
            tasks.append({
                'device': x.BlindsTask.device,
                'action': x.BlindsTask.action,
                'time': x.BlindsTask.time,
                'user': x.name,
                'task_id': x.BlindsTask.id
            })
        
        SHOW_SCHEDULED_TASKS = True
        if SHOW_SCHEDULED_TASKS:
            for x in scheduled_task_query_result:
                tasks.append({
                    'device': x.device,
                    'action': x.action,
                    'time': x.time,
                    'user': 'Automat',
                    'task_id': x.id
                })

        tasks = sorted(tasks, key=lambda k : k['time'])
        for x in tasks:
            x['time'] = unixtime_to_strftime(x['time'], '%d-%m-%Y %H:%M')

        schedule_query_result = BlindsSchedule\
            .query\
            .filter(BlindsSchedule.device.in_(blinds_id_list)) \
            .join(User) \
            .add_column(User.name) \
            .order_by(BlindsSchedule.id) \
            .all()

        schedule = [{
            'id': x.BlindsSchedule.id,
            'device': x.BlindsSchedule.device,
            'action': x.BlindsSchedule.action,
            'hour_type': x.BlindsSchedule.hour_type,
            'time_offset_sign': (('   ', '+ ')
                                 [x.BlindsSchedule.time_offset > 0 and not x.BlindsSchedule.hour_type == 6], '- ')
            [x.BlindsSchedule.time_offset < 0],
            'time_offset': str(timedelta(minutes=abs(x.BlindsSchedule.time_offset)))[:-3],
            'user': x.name
        }for x in schedule_query_result]

        page_name = ('Zarządzaj wieloma roletami',
                     'Zarządzaj roletą "' + names.devices.get(blinds_id_list[0]) + '"')[len(blinds_id_list) == 1]

        page_model = PageModel(page_name, context['user'])\
            .add_breadcrumb_page('Rolety', '/blinds')\
            .add_breadcrumb_page('Zarządzanie roletami', '')\
            .to_dict()

        data_model = {
            'user_tasks': tasks,
            'schedule': schedule,
            'devices': blinds_id_list,
            'names': names
        }
        return render_template('blinds/manage.html', data_model=data_model, page_model=page_model)

    @app.route('/blinds/manage/addTask', methods=['POST'])
    @authorize('user', 'admin')
    def add_blinds_task(context):
        json = request.get_json()

        if not validate_json.validate(validate_json.add_blinds_tasks_schema, json):
            return web_response.bad_request()

        try:
            db.session.bulk_save_objects(list(map(lambda x: BlindsTask(
                    time=json['unix_time'],
                    device=x,
                    action=json['action_id'],
                    user_id=context['user']['id'],
                    timeout=5 * 60,
                    active=True
                ), json['devices_ids'])
            ))
            db.session.commit()
        except:
            return web_response.database_error()

        return web_response.blind_task_added()

    @app.route('/blinds/manage/addSchedule', methods=['POST'])
    @authorize('user', 'admin')
    def add_blinds_schedule(context):
        json = request.get_json()

        if not validate_json.validate(validate_json.add_blinds_schedule_schema, json):
            return web_response.bad_request()

        try:
            db.session.bulk_save_objects(list(map(lambda x: BlindsSchedule(
                    device=x,
                    action=json['action_id'],
                    hour_type=json['hour_type'],
                    time_offset=json['time_offset'],
                    user_id=context['user']['id']
                ), json['devices_ids'])
            ))

            db.session.commit()
        except:
            return web_response.database_error()

        return web_response.blinds_schedule_added()

    @app.route('/blinds/manage/deleteTask', methods=['POST'])
    @authorize('user', 'admin')
    def delete_blinds_task(context):
        json = request.get_json()

        if not validate_json.validate(validate_json.delete_task_schema, json):
            return web_response.bad_request()

        try:
            BlindsTask.query.filter_by(id=json['task_id']).delete()
            db.session.commit()
        except:
            return web_response.database_error()

        return web_response.blinds_task_deleted()

    @app.route('/blinds/manage/deleteSchedule', methods=['POST'])
    @authorize('user', 'admin')
    def delete_blinds_schedule(context):
        json = request.get_json()

        if not validate_json.validate(validate_json.delete_schedule_schema, json):
            return web_response.bad_request()

        try:
            BlindsSchedule.query.filter_by(id=json['schedule_id']).delete()
            db.session.commit()
        except:
            return web_response.database_error()

        return web_response.blinds_schedule_deleted()

    @app.route('/blinds/manage/instantAction', methods=['POST'])
    @authorize('user', 'admin')
    def blinds_instant_action(context):
        json = request.get_json()

        if not validate_json.validate(validate_json.blind_instant_action_schema, json):
            return web_response.bad_request()

        for device_id in json['device_ids']:
            asylumd_client.shutterAction(device_id - 1, json['action_id'] - 1)

        return web_response.blinds_action_executed()
