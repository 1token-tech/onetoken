import asyncio

import ots


def on_update(tk: ots.Tick):
    print(tk)
    print(tk.to_dict())


async def sub_func():
    contract = 'okex/ltc.btc'
    await ots.quote.subscribe_tick(contract, on_update)

    while True:
        await asyncio.sleep(2)


async def get_last():
    contract = 'binance/btc.usdt'

    while True:
        await asyncio.sleep(2)
        tk = await ots.quote.get_last_tick(contract)
        print(tk)


async def main():
    # await sub_func()
    await get_last()


if __name__ == '__main__':
    import logging

    ots.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
