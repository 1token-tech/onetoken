import asyncio

import logging
import aiohttp
import onetoken as ot
from onetoken import Tick


def on_update_1(tk: Tick):
    print('tick come 1', tk)


def on_update_2(tk: Tick):
    print('tick come 2', tk)


async def subscribe_from_ws():
    contract = 'okex/btc.usdt'
    await ot.quote.subscribe_tick(contract, on_update_1)

    contract = 'okex/btc.usdt'
    await ot.quote.subscribe_tick(contract, on_update_2)

    contract = 'binance/eth.btc'
    await ot.quote.subscribe_tick(contract, on_update_2)


async def get_last():
    contract = 'binance/btc.usdt'

    while True:
        await asyncio.sleep(2)
        tk, err = await ot.quote.get_last_tick(contract)
        print('tick get by last', tk, err)


async def main():
    cons, err = await ot.quote.get_contracts('binance')
    print(cons, err)
    con, err = await ot.quote.get_contract('binance/btc.usdt')
    print(con, err)

    await subscribe_from_ws()
    await get_last()
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    print('ots folder', ot)
    print('ots version', ot.__version__)
    print('aiohttp version', aiohttp.__version__)
    ot.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
