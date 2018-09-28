from schema import Schema, And
import time
import re

from asylum.core import names


def validate(schema, json):
    try:
        schema.validate(json)
        return True
    except:
        return False


def validate_register(json):
    try:
        Schema(
            {
                'login': lambda x: re.match('^[a-zA-Z0-9]{3,20}$', x) is not None,
                'name': lambda x: re.match('^[a-zA-Z0-9]{3,20}$', x) is not None,
                'password': lambda x: re.match('^(?=.*[A-Za-z])(?=.*\d)[\S]{8,}$', x) is not None,
                'repassword': str,
                'role': lambda x: x in ['admin', 'user', 'guest']
            }
        ).validate(json)

        if not json['password'] == json['repassword']:
            return False

        return True
    except:
        return False


add_blinds_tasks_schema = Schema(
    {
        'devices_ids': And(lambda x: len(x) > 0,
                           [
                               And(int, lambda x: names.devices.get(x))
                           ]),
        'unix_time': And(int, lambda x: x > time.time()),
        'action_id': And(int, lambda x: names.actions.get(x))
    }
)

add_blinds_schedule_schema = Schema(
    {
        'devices_ids': And(lambda x: len(x) > 0,
                           [
                               And(int, lambda x: names.devices.get(x))
                           ]),
        'action_id': And(int, lambda x: names.actions.get(x)),
        'hour_type': And(int, lambda x: names.hour_types.get(x)),
        'time_offset': int
    }
)

delete_task_schema = Schema(
    {
        'task_id': int
    }
)

delete_schedule_schema = Schema(
    {
        'schedule_id': int
    }
)

login_schema = Schema(
    {
        'login': str,
        'password': str
    }
)

