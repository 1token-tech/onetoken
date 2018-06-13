import asyncio
import logging
import aiohttp
import os

import onetoken as ot
import yaml
from onetoken import Account, log

demo_args = {
    'OT_KEY': '',
    'OT_SECRET': '',
    'account': 'mock/test',
    'conract': 'mock/test',
}


def load_api_key_secret():
    path = os.path.expanduser('~/.onetoken/config.yml')
    if os.path.isfile(path):
        try:
            js = yaml.load(open(path).read())
            if 'ot_key' in js:
                return js['ot_key'], js['ot_secret'], js['account']
            return js['api_key'], js['api_secret'], js['account']
        except:
            log.exception('failed load api key/secret')
    return None, None, None


async def main():
    ot_key, ot_secret, account = load_api_key_secret()
    if ot_key is None or ot_secret is None:
        file_path = '~/.onetoken/config.yml'
        try:
            config = yaml.load(open(os.path.expanduser(file_path)).read())
            if 'ot_key' in config:
                ot_key = config['ot_key']
                ot_secret = config['ot_secret']
                account = config['account']
            else:
                ot_key = config['api_key']
                ot_secret = config['api_secret']
                account = config['account']
        except:
            print('file not found: ', os.path.expanduser(file_path))
            print('input manually:')
            ot_key = input('ot-key: ')
            ot_secret = input('ot-secret: ')
            account = input('account: ')
    acc = Account(account, ot_key, ot_secret)
    await asyncio.sleep(5)
    log.info('Initialized account {}'.format(account))

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
    p_list, err = await acc.get_order_list()
    if err:
        log.warning('Get pending list failed...', err)
    else:
        log.info(f'Pending list: {p_list}')
    #
    # # 获取指定 order 的 info
    # o_info_2, err = await acc.get_order_use_exchange_oid('huobip/qtum.usdt-1786556131')
    # if err:
    #     log.warning('Get order info failed...', err)
    # else:
    #     log.info(f'Order information by exchange_oid: {o_info_2}')
    #
    # await asyncio.sleep(5)
    #
    # # 下单
    # contract_symbol = 'huobip/btc.usdt'
    # contract_symbol_2 = 'huobip/iost.usdt'
    #
    # coid = util.rand_client_oid(contract_symbol)  # client oid 为预设下单 id，方便策略后期跟踪
    # order_1, err = await acc.place_order(con=contract_symbol, price=20000, bs='s', amount=0.01)
    # if err:
    #     log.warning('Place order failed...', err)
    # else:
    #     log.info(f'New order: {order_1}')
    # await asyncio.sleep(0.5)
    #
    # order_2, err = await acc.place_order(con=contract_symbol_2, price=10000, bs='s', amount=1.3)
    # if err:
    #     log.warning('Place order failed...', err)
    # else:
    #     log.info(f'New order: {order_2}')
    # await asyncio.sleep(3)
    #
    # # 获取指定 order 的 info
    # o_info_1, err = await acc.get_order_use_client_oid(order_1['client_oid'])
    # if err:
    #     log.warning('Get order info failed...', err)
    # else:
    #     log.info(f'Order information by client_oid: {o_info_1}')
    #
    # o_info_2, err = await acc.get_order_use_exchange_oid(order_2['exchange_oid'])
    # if err:
    #     log.warning('Get order info failed...', err)
    # else:
    #     log.info(f'Order information by exchange_oid: {o_info_2}')
    #
    # # 获取当前开放的 orders
    # p_list, err = await acc.get_order_list()
    # if err:
    #     log.warning('Get pending list failed...', err)
    # else:
    #     log.info(f'Pending list: {p_list}')
    #
    # # 撤单
    # res, err = await acc.cancel_use_client_oid(order_1['client_oid'])
    # if err:
    #     log.warning('cancel order failed...', err)
    # else:
    #     log.info(f'Canceled order: {res}')
    # res, err = await acc.cancel_use_exchange_oid(order_2['exchange_oid'])
    # if err:
    #     log.warning('cancel order failed...', err)
    # else:
    #     log.info(f'Canceled order: {res}')
    #
    # # add more orders
    # order_more, err = await acc.place_order(con=contract_symbol, price=20000, bs='s', amount=0.1)
    # if err:
    #     log.warning('Place order failed...', err)
    # else:
    #     log.info(f'New order: {order_more}')
    # order_more, err = await acc.place_order(con=contract_symbol_2, price=20000, bs='s', amount=1.2)
    # if err:
    #     log.warning('Place order failed...', err)
    # else:
    #     log.info(f'New order: {order_more}')

    # # # 测试cancel_all 谨慎调用!
    # # await acc.cancel_all()
    # # p_list, err = await acc.get_order_list()
    # # if err:
    # #     log.warning('Get pending list failed...', err)
    # # else:
    # #     log.info(f'Pending list: {p_list}')
    #
    # # 测试place_and_cancel
    # res, err = await acc.place_and_cancel(con=contract_symbol, price=20000, bs='s', amount=0.01, sleep=2)
    # if err:
    #     log.warning('cancel order failed...', err)
    # else:
    #     log.info(f'Placed and canceled order: {res}')
    #
    # # 获取当前开放的 orders
    # p_list, err = await acc.get_order_list()
    # if err:
    #     log.warning('Get pending list failed...', err)
    # else:
    #     log.info(f'Pending list: {p_list}')

    acc.close()


if __name__ == '__main__':
    ot.log_level(logging.INFO)
    print('ots folder', ot)
    print('ots version', ot.__version__)
    print('aiohttp version', aiohttp.__version__)
    asyncio.get_event_loop().run_until_complete(main())
