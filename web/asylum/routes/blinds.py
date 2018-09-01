from flask import render_template, request, make_response, jsonify, redirect, url_for
import time
from datetime import timedelta

from asylum.core import names
from asylum.core.utilities import unixtime_to_strftime
from asylum.core.auth import authorize
from asylum.core.page_model import PageModel

from asylum.models import db
from asylum.models.blinds import BlindsTask, BlindsSchedule
from asylum.models.user import User


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
            return redirect(url_for('blinds_index'), code=302)

        task_query_result = BlindsTask\
            .query \
            .filter(BlindsTask.device.in_(blinds_id_list))\
            .join(User)\
            .add_column(User.name)\
            .order_by(BlindsTask.time)\
            .all()

        schedule_query_result = BlindsSchedule\
            .query\
            .filter(BlindsSchedule.device.in_(blinds_id_list)) \
            .join(User) \
            .add_column(User.name) \
            .order_by(BlindsSchedule.id) \
            .all()

        user_tasks = [{
                'device': x.BlindsTask.device,
                'action': x.BlindsTask.action,
                'time': unixtime_to_strftime(x.BlindsTask.time, '%d-%m-%Y %H:%M'),
                'user': x.name,
                'task_id': x.BlindsTask.id
            } for x in task_query_result]

        schedule = [{
            'id': x.BlindsSchedule.id,
            'device': x.BlindsSchedule.device,
            'action': x.BlindsSchedule.action,
            'hour_type': x.BlindsSchedule.hour_type,
            'time_offset_sign': (('   ', '+ ')[x.BlindsSchedule.time_offset > 0], '- ')[x.BlindsSchedule.time_offset < 0],
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
            'user_tasks': user_tasks,
            'schedule': schedule,
            'devices': blinds_id_list,
            'names': names
        }
        return render_template('blinds/manage.html', data_model=data_model, page_model=page_model)

    @app.route('/blinds/manage/addTask', methods=['POST'])
    @authorize('user', 'admin')
    def add_blinds_task(context):
        post_data = request.get_json()

        if post_data is None \
                or 'devices' not in post_data \
                or 'timedate' not in post_data \
                or 'action' not in post_data \
                or type(post_data['devices']) is not list \
                or not names.actions.get(post_data['action']) \
                or type(post_data['timedate']) is not int \
                or post_data['timedate'] < time.time():
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        devices_list = list(
            map(lambda x: int(x), list(
                filter(lambda x: x.isdigit() and names.devices.get(int(x)), post_data['devices']))
                )
        )

        if len(devices_list) == 0:
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        try:
            for device in devices_list:
                task = BlindsTask(
                    time=post_data['timedate'],
                    device=device,
                    action=post_data['action'],
                    user_id=context['user']['id'],
                    timeout=5,
                    active=True
                )
                db.session.add(task)

            db.session.commit()
        except:
            response = {
                'status': 'error',
                'code': 2
            }
            return make_response(jsonify(response)), 400

        response = {
            'status': 'success',
            'code': 0
        }
        return make_response(jsonify(response)), 201

    @app.route('/blinds/manage/addSchedule', methods=['POST'])
    @authorize('user', 'admin')
    def add_blinds_schedule(context):
        post_data = request.get_json()

        if post_data is None \
                or 'devices' not in post_data \
                or 'hour_type' not in post_data \
                or 'time_offset' not in post_data \
                or 'action' not in post_data \
                or type(post_data['devices']) is not list \
                or names.actions.get(post_data['action'], 'fail') == 'fail' \
                or names.hour_types.get(post_data['hour_type'], 'fail') == 'fail' \
                or type(post_data['time_offset']) is not int:
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        devices_list = list(
            map(lambda x: BlindsSchedule(
                    device=x,
                    action=post_data['action'],
                    hour_type=post_data['hour_type'],
                    time_offset=post_data['time_offset'],
                    user_id=context['user']['id']
                ), list(
                filter(lambda x: x.isdigit() and names.devices.get(int(x)), post_data['devices']))
                )
        )

        if len(devices_list) == 0:
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        try:
            map(lambda x: db.session.add(x), devices_list)
            db.session.commit()
        except:
            response = {
                'status': 'error',
                'code': 2
            }
            return make_response(jsonify(response)), 400

        response = {
            'status': 'success',
            'code': 0
        }
        return make_response(jsonify(response)), 201

    @app.route('/blinds/manage/deleteTask', methods=['POST'])
    @authorize('user', 'admin')
    def delete_blinds_task(context):
        post_data = request.get_json()

        if post_data is None \
                or 'task_id' not in post_data \
                or type(post_data['task_id']) is not int:

            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        try:
            BlindsTask.query.filter_by(id=post_data['task_id']).delete()
            db.session.commit()
        except:
            response = {
                'status': 'error',
                'code': 2
            }
            return make_response(jsonify(response)), 400

        response = {
            'status': 'success',
            'code': 0
        }
        return make_response(jsonify(response)), 200

    @app.route('/blinds/manage/deleteSchedule', methods=['POST'])
    @authorize('user', 'admin')
    def delete_blinds_schedule(context):
        post_data = request.get_json()
        if post_data is None \
                or 'schedule_id' not in post_data \
                or type(post_data['schedule_id']) is not int:

            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        try:
            BlindsSchedule.query.filter_by(id=post_data['schedule_id']).delete()
            db.session.commit()
        except:
            response = {
                'status': 'error',
                'code': 2
            }
            return make_response(jsonify(response)), 400

        response = {
            'status': 'success',
            'code': 0
        }
        return make_response(jsonify(response)), 200
