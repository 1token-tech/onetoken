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
        import json
        file_path = '~/.onetoken/ot_huobip.tyz.json'
        try:
            config = json.loads(open(os.path.expanduser(file_path)).read())
            api_key = config['api_key']
            api_secret = config['api_secret']
            account = config['account']
        except:
            print('file not found: ', os.path.expanduser(file_path))
            print('input manually:')
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

    # 获取当前开放的 orders
    p_list, err = await acc.get_pending_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(f'Pending list: {p_list}')

    # 获取指定 order 的 info
    o_info_2, err = await acc.get_order_use_exchange_oid('huobip/qtum.usdt-1786556131')
    if err:
        log.warning('Get order info failed...', err)
    else:
        log.info(f'Order information by exchange_oid: {o_info_2}')

    # 下单
    contract_symbol = 'huobip/btc.usdt'
    contract_symbol_2 = 'huobip/iost.usdt'

    coid = util.rand_client_oid(contract_symbol)  # client oid 为预设下单 id，方便策略后期跟踪
    order_1, err = await acc.place_order(con=contract_symbol, price=20000, bs='s', amount=0.01)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_1}')
    await asyncio.sleep(0.5)

    order_2, err = await acc.place_order(con=contract_symbol_2, price=10000, bs='s', amount=1.3)
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
    order_more, err = await acc.place_order(con=contract_symbol, price=20000, bs='s', amount=0.1)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_more}')
    order_more, err = await acc.place_order(con=contract_symbol_2, price=20000, bs='s', amount=1.2)
    if err:
        log.warning('Place order failed...', err)
    else:
        log.info(f'New order: {order_more}')

    # # 测试cancel_all 谨慎调用!
    # await acc.cancel_all()
    # p_list, err = await acc.get_pending_list()
    # if err:
    #     log.warning('Get pending list failed...', err)
    # else:
    #     log.info(f'Pending list: {p_list}')

    # 测试place_and_cancel
    res, err = await acc.place_and_cancel(con=contract_symbol, price=20000, bs='s', amount=0.01, sleep=2)
    if err:
        log.warning('cancel order failed...', err)
    else:
        log.info(f'Placed and canceled order: {res}')

    # 获取当前开放的 orders
    p_list, err = await acc.get_pending_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(f'Pending list: {p_list}')

    withdraw_address = ''
    res, err = await acc.post_withdraw(currency='iost', amount=1.3, address=withdraw_address, fee=None)
    if err:
        log.warning('Post withdraw failed...', err)
    else:
        log.info(f'New withdraw: {res}')

    res, err = await acc.cancel_withdraw_use_client_wid(res['client_wid'])
    if err:
        log.warning('Cancel withdraw by client_wid failed...', err)
    else:
        log.info(f'Cancel withdraw by client_wid: {res}')

    res, err = await acc.cancel_withdraw_use_exchange_wid(res['exchange_wid'])
    if err:
        log.warning('Cancel withdraw by exchange_wid failed...', err)
    else:
        log.info(f'Cancel withdraw by exchange_wid: {res}')

    # 未实现的方法
    # status = await acc.get_status()
    # await acc.amend_order_use_client_oid()
    # await acc.amend_order_use_exchange_oid()

    acc.close()


if __name__ == '__main__':
    import logging

    ot.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
