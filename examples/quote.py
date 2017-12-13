import asyncio

from btp import Quote


async def main():
    contract = 'btc.usd:xtc.bitfinex'
    quote = Quote()
    await quote.init()
    await quote.subscribe_tick(contract)

    while True:
        await asyncio.sleep(2)
        tk = quote.get_last_tick(contract)
        print(tk)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
