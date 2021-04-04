import requests

from asylum import config


def open_gate():
    try:
        data = requests.get(config['SUBSYSTEMS']['gate_controller_url'] + "gate", timeout=3).json()
        return True
    except (requests.exceptions.RequestException, ValueError) as e:
        return None
