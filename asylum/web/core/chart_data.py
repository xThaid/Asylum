import json
import datetime

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
