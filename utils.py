from auto_updater import AutoUpdater, get_git_root
import requests
from requests.exceptions import RequestException


def self_update():
    try:
        requests.get('http://127.0.0.1:10100/update')
    except RequestException as ex:
        pass

    AutoUpdater(
        'master',
        get_git_root(__file__),
    ).run()