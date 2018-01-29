import asyncio
import aiohttp
import json

from .logger import log
from .model import Tick

HOST = 'wss://1token.trade/api/v1/quote/ws'


class Quote:
    def __init__(self):
        self.sess = None
        self.ws = None
        self.last_tick_dict = {}
        self.tick_queue = {}
        self.running = False

    async def init(self):
        log.debug('Connecting to {}'.format(HOST))

        try:
            self.sess = aiohttp.ClientSession()
            self.ws = await self.sess.ws_connect(HOST, autoping=False)
            await self.ws.send_json({'uri': 'auth', 'sample-rate': 0})
        except Exception as e:
            log.warning('try connect to WebSocket failed...', e)
            self.sess.close()
            raise e
        else:
            log.debug('Connected to WS')
            self.running = True
            asyncio.ensure_future(self.on_msg())

    async def on_msg(self):
        while not self.ws.closed:
            msg = await self.ws.receive()
            try:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # print(msg.data)
                    self.parse_tick(msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    log.debug('closed')
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.warning('error', msg)
                    break
            except Exception as e:
                log.warning('msg error...', e)

        self.running = False
        log.info('ws was disconnected...')

    # await ws.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': 'btc.usd:xtc.bitfinex'})

    def parse_tick(self, plant_data):
        try:
            data = json.loads(plant_data)
            # print(data)
            if 'uri' in data and data['uri'] == 'single-tick-verbose':
                tick = Tick.from_dict(data['data'])
                self.last_tick_dict[tick.simple_contract] = tick
                if tick.simple_contract in self.tick_queue:
                    self.tick_queue[tick.simple_contract].put_nowait(tick)
        except Exception as e:
            log.warning('parse error', e)

    async def subscribe_tick(self, contract, on_update=None):
        log.info('subscribe tick', contract)
        while not self.running:
            await asyncio.sleep(1)
        if self.ws:
            try:
                await self.ws.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': contract})
            except Exception as e:
                log.warning('subscribe {} failed...'.format(contract), e)
            else:
                self.tick_queue[contract] = asyncio.Queue()
                if on_update:
                    asyncio.ensure_future(self.handle_q(contract, on_update))
        else:
            log.warning('ws is not ready yet...')

    async def handle_q(self, contract, on_update):
        while contract in self.tick_queue:
            q = self.tick_queue[contract]
            tk = await q.get()
            if on_update:
                if asyncio.iscoroutinefunction(on_update):
                    await on_update(tk)
                else:
                    on_update(tk)

    # async def get_last_tick(self, contract):
    #     while not self.running:
    #         await asyncio.sleep(1)
    #     await self.subscribe_tick(contract)
    #     while contract not in self.last_tick_dict:
    #         log.warning(f'tick not ready {contract}')
    #         await asyncio.sleep(1)
    #     return self.last_tick_dict[contract]


_client_pool = {}


async def get_client(key='defalut'):
    if key in _client_pool:
        return _client_pool[key]
    else:
        c = Quote()
        _client_pool[key] = c
        await c.init()
        return c


async def get_last_tick(contract):
    c = await get_client()
    return await c.get_last_tick(contract)


async def subscribe_tick(contract, on_update):
    c = await get_client()
    return await c.subscribe_tick(contract, on_update)
