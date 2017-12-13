import asyncio
import aiohttp
import json

from btp import Ticker


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect('http://localhost:3000/ws') as ws:
        print('connected', ws)
        await ws.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': 'btc.usd:xtc.bitfinex'})
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)
                    parse_tick(msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print('closed')
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('error', msg)
                    break
        except KeyboardInterrupt:
            print('keyboard interrupt')
            ws.close()


def parse_tick(plant_data):
    try:
        data = json.loads(plant_data)
        tick = Ticker.from_dict_v2(data['data'])
        print(tick)
    except:
        print('parse error')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
