from flask import render_template, make_response, jsonify, redirect, url_for

from asylum.web.core.page_model import PageModel
from asylum.web.core.utilities import average_in, round_in
from asylum.web.models.meteo import Meteo
from asylum.web.core.auth import authorize
from asylum.meteo import meteo_data
from asylum.web.core.chart_data import ChartData, group_data

import datetime

MIN_DATE = datetime.date(2019, 1, 4)

def init_meteo_routes(app):

    @app.route('/meteo')
    @app.route('/meteo/')
    @authorize('guest', 'user', 'admin')
    def meteo_redirect(context):
        return redirect(url_for('meteo_now'), code=302)

    @app.route('/meteo/now', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def meteo_now(context):
        page_model = PageModel('Stacja meteo - strona główna', context['user'])\
            .add_breadcrumb_page('Stacja meteo', '/meteo/now')\
            .to_dict()
        data_model = {
            'MIN_DATE': MIN_DATE.strftime('%Y-%m-%d')
        }
        return render_template('meteo/now.html', page_model=page_model, data_model=data_model)

    @app.route('/meteo/getCurrentDustData', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def get_current_dust_data(context):
        current_data = meteo_data.get_data()

        if current_data is None:
            return make_response('', 500)

        return jsonify({
            'dust_PM10': current_data['dust_PM10'],
            'dust_PM25': current_data['dust_PM25'],
            'dust_PM100': current_data['dust_PM100']
        })


    @app.route('/meteo/getCurrentData', methods=['GET'])
    @authorize('guest', 'user', 'admin')
    def get_current_meteo_data(context):
        current_data = meteo_data.get_data()

        if current_data is None:
            return make_response('', 500)

        temperature_delta = 0
        humidity_delta = 0
        pressure_delta = 0

        last_data = Meteo.query\
        .filter(Meteo.time > ((datetime.datetime.now().timestamp()) - (60 * 60)))\
        .first()

        if last_data is not None:
            temperature_delta = int(current_data['temperature']) - last_data.temperature
            humidity_delta = int(current_data['humidity']) - last_data.humidity
            pressure_delta = int(current_data['pressure']) - last_data.pressure

        return jsonify({
            'temperature': current_data['temperature'],
            'temperature_delta': temperature_delta,
            'humidity': current_data['humidity'],
            'humidity_delta': humidity_delta,
            'pressure': current_data['pressure'],
            'pressure_delta': pressure_delta,
            'dust_PM10': current_data['dust_PM10'],
            'dust_PM25': current_data['dust_PM25'],
            'dust_PM100': current_data['dust_PM100']
        })

    @app.route('/meteo/day', defaults={'date': None})
    @app.route('/meteo/day/<string:date>')
    @authorize('guest', 'user', 'admin')
    def meteo_history_day(context, date):
        try:
            date_sanitized = date if date is not None else datetime.datetime.now().strftime('%Y-%m-%d')
            start_time = datetime.datetime.strptime(date_sanitized, '%Y-%m-%d')
        except ValueError:
            return redirect(url_for('meteo_history_day'), code=302)

        if MIN_DATE > start_time.date() or start_time.date() > datetime.date.today():
            return redirect(url_for('meteo_history_day'), code=302)

        grouped_data = group_data(start_time, Meteo, [5])

        meteo_data = {
            'temperature': [],
            'humidity': [],
            'pressure': [],
            'dust': []
        }
        if grouped_data['groups'] is not None:
            for x in grouped_data['groups'][0]:
                meteo_data['temperature'].append(round_in(average_in(map(lambda x: x.temperature / 100, x)), 1))
                meteo_data['humidity'].append(round_in(average_in(map(lambda x: x.humidity / 100, x)), 1))
                meteo_data['pressure'].append(round_in(average_in(map(lambda x: x.pressure / 100, x)), 1))
                meteo_data['dust'].append(round_in(average_in(map(lambda x: x.dust_PM25, x)), 1))

        temperature_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points'][0]]) \
            .add_dataset('Temperatura', meteo_data['temperature'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        humidity_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points'][0]]) \
            .add_dataset('Wilgotność', meteo_data['humidity'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        pressure_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points'][0]]) \
            .add_dataset('Ciśnienie atmosferyczne', meteo_data['pressure'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        dust_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points'][0]]) \
            .add_dataset('Pył PM2.5', meteo_data['dust'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        average_values={
            "temperature": average_in(meteo_data['temperature']),
            'humidity':average_in(meteo_data['humidity']),
            'pressure': average_in(meteo_data['pressure']),
            'dust': average_in(meteo_data['dust'])
        }

        data_model={
            'temperature_chart_data': temperature_chart_data,
            'humidity_chart_data': humidity_chart_data,
            'pressure_chart_data':pressure_chart_data,
            'dust_chart_data': dust_chart_data,
            'average_values': average_values
        }

        page_model = PageModel('Meteo - historia dnia ' + date_sanitized, context['user']) \
            .add_breadcrumb_page('Meteo', '/meteo/now') \
            .add_breadcrumb_page('Historia dnia', '/meteo/day') \
            .to_dict()

        return render_template('meteo/history.html', data_model=data_model, page_model=page_model)
