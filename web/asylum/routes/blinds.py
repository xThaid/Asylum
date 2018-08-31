from flask import render_template, request, make_response, jsonify, redirect, url_for
import time
from datetime import timedelta

from asylum.core import names
from asylum.core.utilities import unixtime_to_strftime
from asylum.core.auth import authorize

from asylum.models import db
from asylum.models.blinds import BlindsTask, BlindsSchedule
from asylum.models.user import User


def init_blinds_routes(app):
    @app.route('/blinds', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def blinds_index(context):
        model = {
            'devices_names': names.devices_names,
            'page_name': 'Rolety',
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Rolety',
                    'href': '/blinds'
                }
            ]
        }
        return render_template('blinds/index.html', model=model)

    @app.route('/blinds/manage/<string:blinds_id>', methods=['GET'])
    @authorize('user', 'admin')
    def blinds_manage(context, blinds_id):
        blinds_id_list = []
        for x in blinds_id.split(','):
            try:
                blind_id = int(x)
                if names.devices_names.get(blind_id, 'fail') != 'fail':
                    blinds_id_list.append(int(x))
            except ValueError:
                pass

        if len(blinds_id_list) == 0:
            return redirect(url_for('blinds_index'), code=302)

        query_result = BlindsTask\
            .query \
            .filter(BlindsTask.device.in_(blinds_id_list))\
            .join(User)\
            .add_column(User.name)\
            .order_by(BlindsTask.time)\
            .all()

        user_tasks = [{
                'device': x.BlindsTask.device,
                'action': x.BlindsTask.action,
                'time': unixtime_to_strftime(x.BlindsTask.time, '%d-%m-%Y %H:%M'),
                'user': x.name,
                'task_id': x.BlindsTask.id
            } for x in query_result]

        query_result = BlindsSchedule\
            .query\
            .filter(BlindsSchedule.device.in_(blinds_id_list))\
            .order_by(BlindsSchedule.id)

        schedule = [{
            'id': x.id,
            'device': x.device,
            'action': x.action,
            'hour_type': x.hour_type,
            'time_offset': (('   ', '+ ')[x.time_offset > 0], '- ')[x.time_offset < 0] + str(timedelta(minutes=abs(x.time_offset)))[:-3]
        }for x in query_result]

        if len(blinds_id_list) == 1:
            page_name = 'Zarządzaj roletą "' + names.devices_names.get(blinds_id_list[0]) + '"'
        else:
            page_name = 'Zarządzaj wieloma roletami'

        model = {
            'schedule': schedule,
            'devices': blinds_id_list,
            'devices_names': names.devices_names,
            'action_names': names.action_names,
            'hour_type_names': names.hour_type_names,
            'user_tasks': user_tasks,
            'page_name': page_name,
            'user': context['user'],
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Rolety',
                    'href': '/blinds'
                },
                {
                    'name': 'Zarządzanie roletą',
                    'href': '/blinds'
                }

            ]
        }
        return render_template('blinds/manage.html', model=model)

    @app.route('/blinds/manage/addTask', methods=['POST'])
    @authorize('user', 'admin')
    def add_blinds_task(context):
        post_data = request.get_json()
        if post_data is None \
                or 'devices' not in post_data \
                or 'timedate' not in post_data \
                or 'action' not in post_data \
                or type(post_data['devices']) is not list \
                or names.action_names.get(post_data['action'], 'fail') == 'fail' \
                or type(post_data['timedate']) is not int \
                or post_data['timedate'] < time.time():

            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        devices_list = []
        for x in post_data['devices']:
            try:
                device_id = int(x)
                if names.devices_names.get(device_id, 'fail') != 'fail':
                    devices_list.append(int(x))
            except ValueError:
                pass

        if len(devices_list) == 0:
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        try:
            for x in devices_list:
                task = BlindsTask(
                    time=post_data['timedate'],
                    device=x,
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
                or names.action_names.get(post_data['action'], 'fail') == 'fail' \
                or names.hour_type_names.get(post_data['hour_type'], 'fail') == 'fail' \
                or type(post_data['time_offset']) is not int:
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        devices_list = []
        for x in post_data['devices']:
            try:
                device_id = int(x)
                if names.devices_names.get(device_id, 'fail') != 'fail':
                    devices_list.append(int(x))
            except ValueError:
                pass

        if len(devices_list) == 0:
            response = {
                'status': 'error',
                'code': 1
            }
            return make_response(jsonify(response)), 400

        try:
            for x in devices_list:
                task = BlindsSchedule(
                    device=x,
                    action=post_data['action'],
                    hour_type=post_data['hour_type'],
                    time_offset=post_data['time_offset']
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
