import asyncio

from btp import Quote


def on_update(tk):
    print(tk)


async def main():
    contract = 'btc.usd:xtc.bitfinex'
    quote = Quote()
    await quote.init()
    await quote.subscribe_tick(contract, on_update)

    while True:
        await asyncio.sleep(2)
        # tk = quote.get_last_tick(contract)
        # print(tk)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
