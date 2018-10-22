"""
使用方法

git clone https://github.com/1token-trade/onetoken
cd onetoken
python examples/get_historical_candle.py
"""
import random

import requests
import gzip
import json


def fetch_candle(contract, duration, since, until=None):
    params = {
        'contract': contract,
        'duration': duration,
        'since': since,
    }
    if until:
        params['until'] = until
    url = 'https://1token.trade/api/v1/quote/candles'
    print('fetch:', url)
    candles = requests.get(url, params=params).json()
    with open(f'examples/candle-{contract.replace("/", "-")}.json', 'w+') as f:
        for candle in candles:
            f.write(json.dumps(candle) + '\n')


def read_and_print(path):
    with open(path, 'r') as f:
        data = f.read()
        total = len(data.splitlines())
        print('total', total, 'candles')
        print('--------this script will print randomly candles--------------')
        for i, line in enumerate(data.splitlines()):
            try:
                candle = json.loads(line)
                if random.random() < 0.1:
                    print('{}/{}'.format(i, total), candle)
            except:
                pass


if __name__ == '__main__':
    fetch_candle('huobip/btc.usdt', '5m', '2018-02-02T00:00:00Z', '2018-02-03T00:00:00Z')
    read_and_print('examples/candle-huobip-btc.usdt.json')
