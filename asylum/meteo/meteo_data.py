import requests

from asylum import config

ALTITUDE = 233


def get_data():
    try:
        meteo_data = requests.get(config['SUBSYSTEMS']['meteo_url'], timeout=3).json()

        relative_pressure = calc_relative_pressure(int(meteo_data['bmppress']), int(meteo_data['sitemp']) / 10)

        return {
            'cold_device': meteo_data['cold'],
            'temperature': meteo_data['sitemp'],
            'humidity': meteo_data['sihumidity'],
            'pressure': relative_pressure,
            'dust_PM10': meteo_data['pms3'],
            'dust_PM25': meteo_data['pms4'],
            'dust_PM100': meteo_data['pms5']
        }
    except (requests.exceptions.RequestException, ValueError) as e:
        return None


def test_meteo_connection():
    data = get_data()
    return data is not None


def calc_relative_pressure(pressure, temperature):
    f1 = 0.0065 * ALTITUDE
    f2 = 1.0 - (f1 / (f1 + temperature + 273.15))
    f3 = pow(f2, -5.257)
    return int(pressure * f3)
