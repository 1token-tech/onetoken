import asyncio

import ots


def on_update(tk: ots.Tick):
    print('tick come', tk)


async def sub_func():
    contract = 'okex/ltc.btc'
    await ots.quote.subscribe_tick(contract, on_update)


async def get_last():
    contract = 'binance/btc.usdt'

    while True:
        await asyncio.sleep(2)
        tk, err = await ots.quote.get_last_tick(contract)
        print(tk, err)


async def main():
    await sub_func()
    await get_last()


if __name__ == '__main__':
    import logging

    print('ots folder', ots)
    ots.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
