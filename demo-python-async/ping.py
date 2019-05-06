"""
This program is to test network delay between you and 1Token

Usage:
    quote.py [options]

Options:
    --url=<url>    url [default: wss://1token.trade/api/v1/ws/tick]



Alternative urls:
wss://1token.trade/api/v1/ws/ping-pong
wss://api.1token.trade/v1/ws/tick
wss://api.1token.trade/v1/ws/ping-pong
"""

import asyncio

import aiohttp
import arrow

from docopt import docopt as docoptinit


async def main():
    session = aiohttp.ClientSession()
    url = str(docopt['--url'])
    print('connect to', url)
    ws = await session.ws_connect(url)
    while True:
        start = arrow.now()
        r = await ws.send_json({'uri': 'ping'})
        res = await ws.receive()
        print(res)
        print(int((arrow.now() - start).total_seconds() * 1000))
        await asyncio.sleep(1)


if __name__ == '__main__':
    docopt = docoptinit(__doc__)
    asyncio.get_event_loop().run_until_complete(main())
