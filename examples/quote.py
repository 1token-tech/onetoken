"""
Usage:
    quote.py [options]

Options:
    --print-only-delay     Print only delay tick
    --test  test cases
"""

import asyncio

import arrow
import logging
import aiohttp
import onetoken as ot
from onetoken import Tick


class Config:
    print_only_delay = False
    test = False


def on_update_1(tk: Tick):
    delay = (arrow.now() - tk.time).total_seconds()
    if delay > 10:
        logging.warning('tick delay comes')
        print(arrow.now(), 'tick come 1', delay, tk)
    if not Config.print_only_delay:
        print(arrow.now(), 'tick come 1', delay, tk)


def on_update_2(tk: Tick):
    delay = (arrow.now() - tk.time).total_seconds()
    if delay > 10:
        logging.warning('tick delay comes')
        print(arrow.now(), 'tick come 2', delay, tk)
    if not Config.print_only_delay:
        print(arrow.now(), 'tick come 2', delay, tk)


async def subscribe_from_ws():
    # sub_list = ['okex/ltc.btc', 'okex/bch.btc', 'binance/btc.usdt', 'binance/bch.btc', 'binance/eos.btc',
    #             'binance/trx.btc', 'binance/eth.btc', 'binance/ada.btc', 'binance/icx.btc', 'binance/ont.btc',
    #             'binance/arn.btc', 'binance/zrx.btc']
    sub_list = ['okex/ltc.btc', 'okex/bch.btc']
    for contract in sub_list:
        await ot.quote.subscribe_tick(contract, on_update_1)

    contract = 'okex/btc.usdt'
    await ot.quote.subscribe_tick(contract, on_update_2)

    contract = 'binance/eth.btc'
    await ot.quote.subscribe_tick(contract, on_update_2)
    await asyncio.sleep(20)
    logging.warning('i am going to test reconnect')
    await asyncio.sleep(1)
    for q in ot.quote._client_pool.values():
        await q.ws.close()


async def get_last():
    contract = 'binance/btc.usdt'

    while True:
        await asyncio.sleep(2)
        tk, err = await ot.quote.get_last_tick(contract)
        if err:
            logging.warning(err)
            continue
        delay = (arrow.now() - tk.time).total_seconds()
        if delay > 10:
            logging.warning('tick delay on get last')
        if not Config.print_only_delay:
            print(arrow.now(), 'tick get by last', delay, tk, err)


async def main():
    # if you are in China Mianland, you can uncomment the following line to use another host
    ot.Config.change_host()
    cons, err = await ot.quote.get_contracts('binance')
    print(cons, err)
    con, err = await ot.quote.get_contract('binance/btc.usdt')
    print(con, err)

    await subscribe_from_ws()
    await get_last()

    if Config.test:
        await asyncio.sleep(30)
        return
    else:
        while True:
            await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        from docopt import docopt as docoptinit
    except ImportError:
        print('docopt not installed, run the following command first:')
        print('pip install docopt')
        import sys

        sys.exit(1)

    docopt = docoptinit(__doc__)
    Config.print_only_delay = docopt['--print-only-delay']
    Config.test = docopt['--test']
    print('ots folder', ot)
    print('ots version', ot.__version__)
    print('aiohttp version', aiohttp.__version__)
    ot.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
