from flask import render_template, make_response, jsonify, redirect, url_for

from asylum.web.core.page_model import PageModel
from asylum.web.models.meteo import Meteo
from asylum.web.core.auth import authorize
from asylum.meteo import meteo_data
from asylum.web.core.chart_data import ChartData, get_grouped_data

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
        if date is None:
            date_temp = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            date_temp = date
        try:
            start_time = datetime.datetime.strptime(date_temp, '%Y-%m-%d')
        except ValueError:
            return redirect(url_for('meteo_history_day'), code=302)

        if MIN_DATE > start_time.date() or start_time.date() > datetime.date.today():
            return redirect(url_for('meteo_history_day'), code=302)

        grouped_data = get_grouped_data(start_time, Meteo, 5)

        meteo_data = {
            'temperature': [],
            'humidity': [],
            'pressure': [],
            'dust': []
        }

        if grouped_data['grouped_data'] is not None:
            for x in grouped_data['grouped_data']:
                len_x = len(x)
                if len_x  > 0:
                    meteo_data['temperature'].append(round(sum(map(lambda x: x.temperature / 10, x))/len_x , 1))
                    meteo_data['humidity'].append(round(sum(map(lambda x: x.humidity / 10, x))/len_x , 1))
                    meteo_data['pressure'].append(round(sum(map(lambda x: x.pressure / 10, x))/len_x , 1))
                    meteo_data['dust'].append(int(sum(map(lambda x: x.dust_PM25, x))/len_x ))
                else:
                    for y in meteo_data:
                        meteo_data[y].append(None)

        temperature_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points']]) \
            .add_dataset('Temperatura', meteo_data['temperature'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        humidity_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points']]) \
            .add_dataset('Wilgotność', meteo_data['humidity'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        pressure_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points']]) \
            .add_dataset('Ciśnienie atmosferyczne', meteo_data['pressure'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()

        dust_chart_data = ChartData() \
            .set_labels([x.strftime('%H:%M') for x in grouped_data['time_points']]) \
            .add_dataset('Pył PM2.5', meteo_data['dust'], [20, 20, 20, 1], [20, 20, 20, 0.0], False, 2) \
            .to_json()


        page_model = PageModel('Meteo - historia dnia ' + date_temp, context['user']) \
            .add_breadcrumb_page('Meteo', '/meteo/now') \
            .add_breadcrumb_page('Historia dnia', '/meteo/day') \
            .to_dict()

        temp_not_None = list(filter(lambda x: x is not None, meteo_data['temperature']))
        hum_not_None = list(filter(lambda x: x is not None, meteo_data['humidity']))
        press_not_None = list(filter(lambda x: x is not None, meteo_data['pressure']))
        dust_not_None = list(filter(lambda x: x is not None, meteo_data['dust']))

        average_values={
            "temperature": (sum(temp_not_None) / len(temp_not_None)) if len(temp_not_None)>0 else 0,
            'humidity': sum(hum_not_None) / len(hum_not_None) if len(hum_not_None)>0 else 0,
            'pressure': sum(press_not_None) / len(press_not_None) if len(press_not_None)>0 else 0,
            'dust': sum(dust_not_None) / len(dust_not_None) if len(dust_not_None)>0 else 0
        }

        data_model={
            'temperature_chart_data': temperature_chart_data,
            'humidity_chart_data': humidity_chart_data,
            'pressure_chart_data':pressure_chart_data,
            'dust_chart_data': dust_chart_data,
            'average_values': average_values
        }

        return render_template('meteo/history.html', data_model=data_model, page_model=page_model)
