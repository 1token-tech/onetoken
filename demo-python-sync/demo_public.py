"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests


def main():
    res = requests.get('https://1token.trade/api/v1/basic/time')
    pprint(res.json())

    res = requests.get('https://1token.trade/api/v1/basic/support-exchanges-v2')
    pprint(res.json(), width=240)

    res = requests.get('https://1token.trade/api/v1/basic/contracts?exchange=okef')
    pprint(res.json(), width=1000)

    res = requests.get('https://1token.trade/api/v1/quote/ticks?exchange=okef')
    pprint(res.json()[:3], width=1000)

    res = requests.get('https://1token.trade/api/v1/quote/single-tick/okef/btc.usd.q')
    pprint(res.json(), width=1000)

    res = requests.get('https://1token.trade/api/v1/quote/single-tick/okex/btc.usdt')
    pprint(res.json(), width=1000)


if __name__ == '__main__':
    main()
