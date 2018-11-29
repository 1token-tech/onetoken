"""
使用方法

git clone https://github.com/1token-trade/onetoken
cd onetoken
python examples/get_historical_quote.py
"""
import random

import requests
import pandas as pd
import json


def get_contracts(date):
    url = 'http://hist-quote.1tokentrade.cn/zhubi-contracts?date={}'.format(date)
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        print('fail get contracts', r.status_code, r.text)
    print('----------available contracts------------')
    print('total size', len(r.json()))
    print('first 10 contracts', r.json()[:10])


def download(contract, date):
    url = 'http://hist-quote.1tokentrade.cn/zhubis?date={}&contract={}'.format(date, contract)
    print('downloading', url)
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        print('fail get historical tick', r.status_code, r.text)
        return
    block_size = 300 * 1024
    total = 0
    with open('zhubi-{}-{}.csv'.format(date, contract.replace('/', '-')), 'w') as f:
        for data in r.iter_content(block_size):
            f.write(data)
            total += len(data) / 1024
            print('{} {} downloaded {}kb'.format(contract, date, round(total)))


#csv格式，按exchange_time顺序每行为一条逐笔信息
#列数据的类型：['exchange_time', 'contract', 'price', 'bs', 'amount', 'exgtimestamp', 'time', 'timestamp']
def read(path):
    obj = pd.read_csv(path)
    col_names = ['exchange_time', 'contract', 'price', 'bs', 'amount', 'exgtimestamp', 'time', 'timestamp']
    total = 0
    for i, row in obj.iterrows():
        total += 1
        if random.random() < 0.0001:
            msg = '| '
            for j, col in row.iteritems():
                msg += f'{col_names[j]}: {col} | '
            print('msg')


def main():
    date = '2018-02-02'
    get_contracts(date)

    download('huobip/btc.usdt', '2018-11-25')  # this file size is around 15MB

    read('zhubi-2018-11-25-huobip-btc.usdt.gz')


if __name__ == '__main__':
    main()
