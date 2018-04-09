import os
import yaml
from onetoken import Account, util, log


def load_api_key_secret(file_path):
    path = os.path.expanduser(file_path)
    if os.path.isfile(path):
        try:
            f_config = open(path)
            js = yaml.load(f_config.read())
            f_config.close()
            return js['api_key'], js['api_secret'], js['account']
        except:
            log.exception('failed load api key/secret')
    return None, None, None


def input_api_key_secret():
    print('input manually:')
    api_key = input('api_key: ')
    api_secret = input('api_secret: ')
    account = input('account: ')
    return api_key, api_secret, account
