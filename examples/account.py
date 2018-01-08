import asyncio

import btp
from btp import Account, util, log
import json
import os


def load_api_key_secret():
    path = os.path.expanduser('~/.1token/config.js')
    if os.path.isfile(path):
        try:
            js = json.loads(open(path).read())
            return js['api_key'], js['api_secret']
        except:
            log.exception('failed load api key/secret')
    return None, None


async def main():
    # check_auth_file()
    api_key, api_secret = load_api_key_secret()
    if api_key is None or api_secret is None:
        api_key = input('api_key: ')
        api_secret = input('api_secret: ')
    acc = Account('tyz@huobip', api_key=api_key, api_secret=api_secret)

    # 获取账号 info
    info, err = await acc.get_info()
    if err:
        log.warning('Get info failed...', err)
    else:
        log.info(info)

    # 根据 pos symbol 获取账号 amount
    # 现货类似 btc, bch
    # 期货类似 btc.usd.q
    amount = acc.get_total_amount('btc')
    log.info(amount)

    # 下单
    coid = util.rand_client_oid()  # client oid 为预设下单 id，方便策略后期跟踪
    order, err = await acc.place_order(con='btc.usdt:huobip', price=0.01, bs='b', amount=1, client_oid=coid)
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

    btp.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
