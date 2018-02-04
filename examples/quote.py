import asyncio

import onetoken as ot
from onetoken import Tick


def on_update(tk: Tick):
    print('tick come', tk)


def on_update2(tk: Tick):
    print('tick come 2', tk)


async def sub_func():
    contract = 'okex/ltc.btc'
    await ot.quote.subscribe_tick(contract, on_update)

    contract = 'okex/ltc.btc'
    await ot.quote.subscribe_tick(contract, on_update2)

    contract = 'okex/eth.btc'
    await ot.quote.subscribe_tick(contract, on_update2)


async def get_last():
    contract = 'binance/btc.usdt'

    while True:
        await asyncio.sleep(2)
        tk, err = await ot.quote.get_last_tick(contract)
        print(tk, err)


async def main():
    await sub_func()
    await get_last()


if __name__ == '__main__':
    import logging

    print('ots folder', ot)
    ot.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
