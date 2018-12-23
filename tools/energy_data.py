import re
import requests
import json
import config

ENERGY_IMPORT_OFFSET = 471851
ENERGY_EXPORT_OFFSET = 1124061
ENERGY_PRODUCTION_OFFSET = 1080118640
cfg = config.config


def get_flara_data():
    try:
        res = requests.get(cfg['SUBSYSTEMS']['flara_url'] + "list_en.html", timeout=1).text
        if res != "<tr class='msgfail'><td>Devices not found.</td></tr>":
            res = requests.get(cfg['SUBSYSTEMS']['flara_url'] + "FF00000080087B2E00010102000001EF/data_en.html", timeout=1).text
            return {
                'power': int(re.search("(?<=Active power</div><div class='pvalue vok'>)[0-9]*", res).group()),
                'total_energy': int(float(re.search("(?<=Total energy</div><div class='pvalue vok'>)[0-9.]*", res)
                                          .group()) * 1000 - ENERGY_PRODUCTION_OFFSET)
            }
        else:
            return None

    except (requests.exceptions.RequestException, AttributeError):
        return None


def get_emeter_data():
    try:
        emeter_reading = requests.get(cfg['SUBSYSTEMS']['emeter_url'], timeout=1).json()
        f = open("/run/pi/meter", "w")
        f.write(json.dumps(emeter_reading))

        power_index = ('7', '8', '9')
        power_import = 0
        power_export = 0

        for x in power_index:
            power = int(float(emeter_reading[x]))

            if power < 0:
                power_export += power
            else:
                power_import += power

        return {
            'power_import': power_import,
            'power_export': abs(power_export),
            'total_energy_import': int(float(emeter_reading['37']) * 1000) + ENERGY_IMPORT_OFFSET,
            'total_energy_export': int(float(emeter_reading['38']) * 1000) + ENERGY_EXPORT_OFFSET
        }
    except (requests.exceptions.RequestException, ValueError) as e:
        return None


def get_data():
    emeter_data = get_emeter_data()
    flara_data = get_flara_data()

    if emeter_data is None or flara_data is None:
        return None

    return {
        'power_consumption': max(0, emeter_data['power_import'] + flara_data['power'] - emeter_data['power_export']),
        'power_production': flara_data['power'],
        'total_energy_production': flara_data['total_energy'],
        'power_use': max(0, flara_data['power'] - emeter_data['power_export']),
        'power_import': emeter_data['power_import'],
        'power_export': emeter_data['power_export'],
        'power_store': int(emeter_data['power_export'] * 0.8 - emeter_data['power_import']),
        'total_energy_import': emeter_data['total_energy_import'],
        'total_energy_export': emeter_data['total_energy_export']
    }


def test_flara_connection():
    data = get_flara_data()
    return data is not None


def test_emeter_connection():
    data = get_emeter_data()
    return data is not None
