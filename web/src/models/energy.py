from src.db_models import get_last_rows, to_strftime
from src.db_models.energy import Energy
from src.models.shared import ChartData


class EnergyIndexModel:
    page_name = ''
    chart_data = {}
    current_power = 0
    energy = []
    max_power = 0
    user = {}
    breadcrumb = []

    def __init__(self, context):
        data = get_last_rows(Energy, [Energy.production, Energy.time], 1440, 1440)
        data[1] = to_strftime(data[1], '%H:%M')
        data.append(get_last_rows(Energy, [Energy.production], 11520, 11520)[0][1::1440])
        data[2] = [(y - x) / 1000 for x, y in zip(data[2], data[2][1:])]

        chart_data = ChartData()\
            .set_labels(data[1][1::5])\
            .add_dataset('Produkcja', data[0][1::5], 'rgba(20, 255, 50, 0.8)', 'rgba(40, 255, 70, 0.4)', 1)

        self.chart_data = chart_data.to_json()
        self.current_power = data[0][-1]
        self.energy = data[2]
        self.max_power = max(data[0])
        self.user = context['user']
        self.page_name = 'Energia'
        self.breadcrumb = [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Energia',
                    'href': '/energy'
                }
            ]