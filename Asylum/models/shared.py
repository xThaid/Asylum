import json


class ChartData:
    labels = []
    datasets = []

    def set_labels(self, labels):
        self.labels = labels
        return self

    def add_dataset(self, label, data, border_color, background_color, border_width):
        self.datasets.append({
            'label': label,
            'data': data,
            'borderColor': border_color,
            'backgroundColor': background_color,
            'borderWidth': border_width
        })
        return self

    def to_json(self):
        return json.dumps({
            'labels': self.labels,
            'datasets': self.datasets
        })
