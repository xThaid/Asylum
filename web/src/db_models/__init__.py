from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


def get_last_rows(db_model, attributes, from_date, count):
    power_production = db_model\
        .query.with_entities(db_model.id, *attributes)\
        .order_by(db_model.id.desc())\
        .limit(from_date)\
        .from_self()\
        .order_by(db_model.id)\
        .limit(count)\
        .all()

    data_list = []
    for x in range(1, len(attributes) + 1):
        data_list.append([o[x] for o in power_production])
    return data_list


def to_strftime(time, format_str):
    return [datetime.datetime.fromtimestamp(o).strftime(format_str) for o in time]
