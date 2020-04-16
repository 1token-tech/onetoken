"""
使用方法

git clone https://github.com/1token-trade/onetoken
cd onetoken
python examples/get_historical_quote.py
"""
import gzip
import json
import logging
import os

import requests
import yaml

# 把下面的OT Key换成自己的OT Key, 申请方法如下
# https://1token.trade/account/apis
# https://1token.trade/dataservice
OT_KEY = 'aaaaa-bbbbb-ccccc-ddddd'


def get_contracts(date, quote_type):
    url = 'https://hist-quote.1tokentrade.cn/{}/contracts?date={}'.format(quote_type, date)
    print('get contracts: ', url)
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        print('fail get contracts', r.status_code, r.text)
    print('----------available contracts------------')
    print('total size', len(r.json()))
    print('first 10 contracts', r.json()[:10])


def download(url, file_path):
    print('downloading', url)
    r = requests.get(url, headers={'ot-key': ot_key}, stream=True)
    if r.status_code != 200:
        print('fail get historical data', r.status_code, r.text)
        print('failed ot-key', ot_key[:5], ot_key[-5:], len(ot_key))
        return
    print('quota-remaining:', r.headers.get('ot-quota-remaining'),
          'quota-consumption:', r.headers.get('ot-quota-consumption'))
    block_size = 300 * 1024
    total = 0
    with open(file_path, 'wb') as f:
        for data in r.iter_content(block_size):
            f.write(data)
            total += len(data) / 1024
            print('downloaded {}kb'.format(round(total)))


def download_simple_ticks(contract, date, file_path):
    url = 'https://hist-quote.1tokentrade.cn/ticks/simple?date={}&contract={}'.format(date, contract)
    download(url, file_path)


def download_full_ticks(contract, date, file_path):
    url = 'https://hist-quote.1tokentrade.cn/ticks/full?date={}&contract={}'.format(date, contract)
    download(url, file_path)


def download_zhubis(contract, date, file_path):
    url = 'https://hist-quote.1tokentrade.cn/trades?date={}&contract={}'.format(date, contract)
    download(url, file_path)


def download_and_print_candles(contract, since, until, duration):
    # support format: json & csv, default json
    url = 'https://hist-quote.1tokentrade.cn/candles?since={}&until={}&contract={}&duration={}&format=json'.format(
        since, until, contract, duration)
    print('downloading', url)
    resp = requests.get(url, headers={'ot-key': ot_key})
    if resp.status_code != 200:
        print('fail get candles', resp.status_code, resp.text)
        return
    r = resp.json()
    total = len(r)
    print('total', total, 'data')
    print('quota-remaining:', resp.headers.get('ot-quota-remaining'),
          'quota-consumption:', resp.headers.get('ot-quota-consumption'))
    print('--------this script will print all  data--------------')
    for i, candle in enumerate(r):
        print('{}/{}'.format(i, total), json.dumps(candle))


def unzip_and_read(path):
    data = open(path, 'rb').read()
    r = gzip.decompress(data).decode()
    total = len(r.splitlines())
    csvpath = path.replace('.gz', '.csv')
    open(csvpath, 'w').write(r)
    print('total', total, 'data')
    print('--------this script will print all data--------------')
    for i, line in enumerate(r.splitlines()):
        try:
            print('{}/{}'.format(i, total), line)
        except:
            pass


def load_otkey():
    if OT_KEY != 'aaaaa-bbbbb-ccccc-ddddd':
        return OT_KEY
    path = os.path.expanduser('~/.onetoken/config.yml')
    if os.path.isfile(path):
        try:
            js = yaml.load(open(path).read())
            if 'ot_key' in js:
                return js['ot_key']
            return js['api_key']
        except:
            logging.exception('failed load otkey')
    return input('input your otkey: ')


def main():
    try:
        os.makedirs('data')
    except:
        pass
    date = '2019-12-12'
    contract = 'okex/eos.eth'

    # simple tick
    # get_contracts(date, 'ticks')
    # file_path = 'data/tick-simple-{}-{}.gz'.format(date, contract.replace('/', '-'))
    # download_simple_ticks(contract, date, file_path)
    # unzip_and_read(file_path)
    #
    # # full tick
    # file_path = 'data/tick-full-{}-{}.gz'.format(date, contract.replace('/', '-'))
    # download_full_ticks(contract, date, file_path)
    # unzip_and_read(file_path)
    #
    # # trades
    # get_contracts(date, 'trades')
    # file_path = 'data/trades-{}-{}.gz'.format(date, contract.replace('/', '-'))
    # download_zhubis(contract, date, file_path)
    # unzip_and_read(file_path)
    #
    # # candle
    since = date
    until = '2019-12-13'
    download_and_print_candles(contract, since, '2020-10-10', '1m')


if __name__ == '__main__':
    ot_key = load_otkey()
    main()
