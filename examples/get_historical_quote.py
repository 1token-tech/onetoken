"""
使用方法

git clone https://github.com/1token-trade/onetoken
cd onetoken
python examples/get_historical_quote.py
"""

import requests
import gzip
import json


def get_contracts():
    r = requests.get('http://alihz-net-0.qbtrade.org/contracts?date=2018-01-02')
    print('----------available contracts------------')
    print(r.json()[:10])


def download(contract, date):
    url = 'http://alihz-net-0.qbtrade.org/hist-ticks?date={}&contract={}'.format(date, contract)
    print('downloading', url)
    r = requests.get(url, stream=True)
    block_size = 100 * 1024
    total = 0
    with open('examples/tick-{}-{}.gz'.format(date, contract.replace('/', '-')), 'wb') as f:
        for data in r.iter_content(block_size):
            f.write(data)
            total += len(data) / 1024
            print('{} {} downloaded {}kb'.format(contract, date, round(total)))


def unzip_and_read(path):
    data = open(path, 'rb').read()
    r = gzip.decompress(data).decode()
    cnt = 0
    for line in r.splitlines():
        try:
            tick = json.loads(line)
            cnt += 1
            if cnt < 10:
                print(tick)
        except:
            pass


if __name__ == '__main__':
    # this file size is about 3.5MB
    download('okex/btc.usdt', '2018-01-02')

    unzip_and_read('examples/tick-2018-01-02-okex-btc.usdt.gz')
