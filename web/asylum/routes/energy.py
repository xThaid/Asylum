from flask import render_template
from asylum.core.auth import authorize
from asylum.core.utilities import unixtime_to_strftime
from asylum.core.chart_data import ChartData
from asylum.models.energy import Energy


def init_energy_routes(app):

    @app.route('/energy', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def energy(context):
        data = Energy.get_last_rows([Energy.production, Energy.time], 1440, 1440)
        data[1] = unixtime_to_strftime(data[1], '%H:%M')
        data.append(Energy.get_last_rows([Energy.production], 11520, 11520)[0][1::1440])
        data[2] = [(y - x) / 1000 for x, y in zip(data[2], data[2][1:])]
        for i in range(3):
            data[i] = [[1, 0], data[i]][data[i] is None]

        chart_data = ChartData()\
            .set_labels(data[1][1::5])\
            .add_dataset('Produkcja', data[0][1::5], 'rgba(20, 255, 50, 0.8)', 'rgba(40, 255, 70, 0.4)', 1)

        model = {
            'chart_data': chart_data.to_json(),
            'current_power': data[0][-1],
            'energy': data[2],
            'max_power': max(data[0]),
            'user': context['user'],
            'page_name': 'Energia',
            'breadcrumb': [
                {
                    'name': 'Strona główna',
                    'href': '/home'
                },
                {
                    'name': 'Energia',
                    'href': '/energy'
                }
            ]
        }

        return render_template('energy.html', model=model)
