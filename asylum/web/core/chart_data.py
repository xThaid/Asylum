import json


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
