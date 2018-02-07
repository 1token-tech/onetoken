import asyncio
import os

import yaml

import onetoken as ot
from onetoken import Account, util, log


def load_api_key_secret():
    path = os.path.expanduser('~/.onetoken/config.yml')
    if os.path.isfile(path):
        try:
            js = yaml.load(open(path).read())
            return js['api_key'], js['api_secret'], js['account']
        except:
            log.exception('failed load api key/secret')
    return None, None, None


async def main():
    # check_auth_file()
    api_key, api_secret, account = load_api_key_secret()
    if api_key is None or api_secret is None:
        api_key = input('api_key: ')
        api_secret = input('api_secret: ')
        account = input('account: ')
    acc = Account(account, api_key=api_key, api_secret=api_secret)

    # 获取账号 info
    info, err = await acc.get_info()
    if err:
        log.warning('Get info failed...', err)
    else:
        log.info(info.data)

    # 根据 pos symbol 获取账号 amount
    # 现货类似 btc, bch
    # 期货类似 btc.usd.q
    amount = info.get_total_amount('btc')
    log.info(amount)

    # 下单
    contract_symbol = 'binance/bnb.eth'
    coid = util.rand_client_oid(contract_symbol)  # client oid 为预设下单 id，方便策略后期跟踪
    order, err = await acc.place_order(con=contract_symbol, price=2, bs='s', amount=0.1, client_oid=coid)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(order)

    await asyncio.sleep(3)

    # 获取指定 order 的 info
    o_info, err = await acc.get_order_use_client_oid(coid)
    if err:
        log.warning('Get order info failed...', err)
    else:
        log.info(o_info)

    # 获取当前开放的 orders
    p_list, err = await acc.get_pending_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(p_list)

    # 撤单
    res, err = await acc.cancel_use_client_oid(coid)
    if err:
        log.warning('cancel order failed...', err)
    else:
        log.info(res)


if __name__ == '__main__':
    import logging

    ot.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
