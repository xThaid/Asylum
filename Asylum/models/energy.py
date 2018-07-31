from Asylum.common_utilities import get_last_rows, to_strftime
from Asylum.db_models.energy import EnergyProduction
from Asylum.models.shared import ChartData


class EnergyIndexModel:
    page_name = 'Energia'
    chart_data = {}
    current_power = 0
    energy = []
    max_power = 0

    def __init__(self):
        data = get_last_rows(EnergyProduction, [EnergyProduction.power, EnergyProduction.time], 1440, 1440)
        data[1] = to_strftime(data[1], '%H:%M')
        data.append(get_last_rows(EnergyProduction, [EnergyProduction.energy], 11520, 11520)[0][1::1440])
        data[2] = [(y - x) / 1000 for x, y in zip(data[2], data[2][1:])]

        chart_data = ChartData()\
            .set_labels(data[1][1::5])\
            .add_dataset('Produkcja', data[0][1::5], 'rgba(20, 255, 50, 0.8)', 'rgba(40, 255, 70, 0.4)', 1)

        self.chart_data = chart_data.to_json()
        self.current_power = data[0][-1]
        self.energy = data[2]
        self.max_power = max(data[0])
