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
        log.info(f'Account info: {info.data}')

    # 根据 pos symbol 获取账号 amount
    # 现货类似 btc, bch
    # 期货类似 btc.usd.q
    currency = 'btc'
    amount = info.get_total_amount(currency)
    log.info(f'Amount: {amount} {currency}')

    # 下单
    contract_symbol = 'huobip/bnb.eth'
    contract_symbol_2 = 'huobip/eth.usdt'

    coid = util.rand_client_oid(contract_symbol)  # client oid 为预设下单 id，方便策略后期跟踪
    order_1, err = await acc.place_order(con=contract_symbol, price=2, bs='s', amount=0.1, client_oid=coid)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_1}')
    await asyncio.sleep(0.5)

    order_2, err = await acc.place_order(con=contract_symbol_2, price=10000, bs='s', amount=0.5)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_2}')
    await asyncio.sleep(3)

    # 获取指定 order 的 info
    o_info_1, err = await acc.get_order_use_client_oid(order_1['client_oid'])
    if err:
        log.warning('Get order info failed...', err)
    else:
        log.info(f'Order information by client_oid: {o_info_1}')

    o_info_2, err = await acc.get_order_use_exchange_oid(order_2['exchange_oid'])
    if err:
        log.warning('Get order info failed...', err)
    else:
        log.info(f'Order information by exchange_oid: {o_info_2}')

    # 获取当前开放的 orders
    p_list, err = await acc.get_pending_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(f'Pending list: {p_list}')

    # 撤单
    res, err = await acc.cancel_use_client_oid(order_1['client_oid'])
    if err:
        log.warning('cancel order failed...', err)
    else:
        log.info(f'Canceled order: {res}')
    res, err = await acc.cancel_use_exchange_oid(order_2['exchange_oid'])
    if err:
        log.warning('cancel order failed...', err)
    else:
        log.info(f'Canceled order: {res}')

    # add more orders
    order_more, err = await acc.place_order(con=contract_symbol, price=2, bs='s', amount=0.1)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_more}')
    order_more, err = await acc.place_order(con=contract_symbol_2, price=2, bs='b', amount=0.3)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_more}')

    # 测试cancel_all
    await acc.cancel_all()
    p_list, err = await acc.get_pending_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(f'Pending list: {p_list}')

    # 测试place_and_cancel
    res, err = await acc.place_and_cancel(con=contract_symbol, price=3, bs='s', amount=0.2, sleep=2)
    if err:
        log.warning('cancel order failed...', err)
    else:
        log.info(f'Placed and canceled order: {res}')

    # 未实现的方法
    # status = await acc.get_status()
    # await acc.amend_order_use_client_oid()
    # await acc.amend_order_use_exchange_oid()

    acc.close()


if __name__ == '__main__':
    import logging

    ot.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
