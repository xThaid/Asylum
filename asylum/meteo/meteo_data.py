import requests

from asylum import config

def get_data():
    try:
        meteo_data = requests.get(config['SUBSYSTEMS']['meteo_url'], timeout=1).json()

        if meteo_data['cold'] == "1":
            return None

        return {
            'temperature': meteo_data['sitemp'],
            'humidity': meteo_data['sihumidity'],
            'pressure': meteo_data['bmppress'],
            'dust_PM10': meteo_data['pms3'],
            'dust_PM25': meteo_data['pms4'],
            'dust_PM100': meteo_data['pms5']
        }
    except (requests.exceptions.RequestException, ValueError) as e:
        return None

def test_meteo_connection():
    data = get_data()
    return data is not None
