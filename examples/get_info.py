import aiohttp
import asyncio


async def main():
    s = aiohttp.ClientSession()
    resp = await s.get('http://api.qbtrade.org/trans/xtc.huobip/leo/info', timeout=15)
    txt = await resp.text()
    print(resp.status_code)
    print(txt)


if __name__ == '__main__':
    asyncio.ensure_future(main())
    asyncio.get_event_loop().run_forever()
