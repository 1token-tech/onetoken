import asyncio

import btp
from btp import log


def on_update(tk):
    print(tk)
    log.info(tk)


async def sub_func():
    contract = 'btc.usd:xtc.bitfinex'
    await btp.quote.subscribe_tick(contract, on_update)

    while True:
        await asyncio.sleep(2)


async def get_last():
    contract = 'btc.usd:xtc.bitfinex'

    while True:
        await asyncio.sleep(2)
        tk = await btp.quote.get_last_tick(contract)
        print(tk)
        log.info(tk)


async def main():
    await get_last()


if __name__ == '__main__':
    import logging
    btp.log_level(logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
