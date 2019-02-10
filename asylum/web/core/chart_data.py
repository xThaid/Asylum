import json
import datetime
from sqlalchemy import and_

def group_data(start_time, model, time_separation):

    time_from_midnight = 24 * 60 * 60
    datetime_now = datetime.datetime.now()

    if (start_time + datetime.timedelta(days=1)) > datetime_now:
        time_from_midnight = datetime_now.timestamp() - datetime_now.replace(hour=0, minute=0, second=0).timestamp()

    if time_from_midnight == 0:
        time_from_midnight = 1

    time_points = []
    for y in time_separation:
        points_count = int(time_from_midnight / (60 * y)) + 1
        time_points.append([(start_time + datetime.timedelta(minutes=x * y))
                             for x in range(points_count - 1)])

    data = model.query.filter(and_(model.time >= start_time.timestamp(), model.time < (start_time + datetime.timedelta(days=1)).timestamp())).all()

    if len(data) == 0:
        return {
            "time_points": time_points,
            'groups': None,
            'non_grouped': None
        }


    grouped_data = []
    for y in range(len(time_separation)):
        grouped_data.append([])
        if start_time + datetime.timedelta(days=1) > datetime_now:
            group_count = int((datetime_now.hour * 60 + datetime_now.minute) / time_separation[y]) + 1
        else:
            group_count = int((24 * 60) / time_separation[y]) + 1

        for x in range(group_count):
            grouped_data[y].append([])

        curr_time = 0
        next_time = start_time + datetime.timedelta(minutes=time_separation[y])

        for entry in data:
            while entry.time >= next_time.timestamp():
                curr_time += 1
                next_time = next_time + datetime.timedelta(minutes=time_separation[y])
            grouped_data[y][curr_time].append(entry)

    return {
        "time_points": time_points,
        "groups": grouped_data,
        'non_grouped': data
    }


class ChartData:
    def __init__(self):
        self.labels = []
        self.datasets = []

    def set_labels(self, labels):
        self.labels = labels
        return self

    def add_dataset(self, label, data, border_color, background_color, hidden=False, border_width=1):


        self.datasets.append({
            'label': label,
            'data': data,
            'borderColor': 'rgba(' + str(border_color[0])
                           + ', ' + str(border_color[1])
                           + ', ' + str(border_color[2])
                           + ', ' + str(border_color[3]) + ')',
            'backgroundColor': 'rgba(' + str(background_color[0])
                           + ', ' + str(background_color[1])
                           + ', ' + str(background_color[2])
                           + ', ' + str(background_color[3]) + ')',
            'borderWidth': border_width,
            'hidden': hidden
        })
        return self

    def to_json(self):
        return json.dumps({
            'labels': self.labels,
            'datasets': self.datasets
        })


class EnergyRecords:
    def __init__(self):
        self.power = {}
        self.energy = {}

    def add_power_record(self, name, record_data):
        self.power[name] = prepare_record_entry(record_data)
        return self

    def add_energy_record(self, name, record_data):
        self.energy[name] = prepare_record_entry(record_data)
        return self

    def build(self):
        return {'max_power': self.power, 'max_energy': self.energy}


def prepare_record_entry(record_entry):
    entry = {
        'value': record_entry[0],
        'day': datetime.date.fromordinal(record_entry[1]).strftime('%Y-%m-%d'),
    }
    return entry
