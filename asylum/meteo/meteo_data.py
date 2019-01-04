import requests

from asylum import config

def get_data():
    try:
        meteo_data = requests.get(config['SUBSYSTEMS']['meteo_url'], timeout=1).json()

        return {
            'temperature': meteo_data[''],
            'humidity': meteo_data[''],
            'pressure': meteo_data[''],
            'dust_PM10': meteo_data[''],
            'dust_PM25': meteo_data[''],
            'dust_PM100': meteo_data['']
        }
    except (requests.exceptions.RequestException, ValueError) as e:
        return None

def test_meteo_connection():
    data = get_data()
    return data is not None
