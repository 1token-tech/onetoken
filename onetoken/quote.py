import asyncio
from collections import defaultdict

import aiohttp
import json

from .logger import log
from .model import Tick

HOST = 'wss://api.1token.trade/v1/quote/ws'


class Quote:
    def __init__(self):
        self.sess = None
        self.ws = None
        self.last_tick_dict = {}
        self.tick_queue_update = defaultdict(list)
        self.tick_queue = {}
        self.running = False
        self.lock = asyncio.Lock()

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
                self.last_tick_dict[tick.contract] = tick
                if tick.contract in self.tick_queue:
                    self.tick_queue[tick.contract].put_nowait(tick)
        except Exception as e:
            log.warning('parse error', e)

    async def subscribe_tick(self, contract, on_update=None):
        log.info('subscribe tick', contract)
        while not self.running:
            await asyncio.sleep(1)
        async with self.lock:
            try:
                if contract not in self.tick_queue:
                    await self.ws.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': contract})
                    self.tick_queue[contract] = asyncio.Queue()
                    if on_update:
                        if not self.tick_queue_update[contract]:
                            asyncio.ensure_future(self.handle_q(contract))
            except Exception as e:
                log.warning('subscribe {} failed...'.format(contract), e)
            else:
                if on_update:
                    self.tick_queue_update[contract].append(on_update)

    async def handle_q(self, contract):
        while contract in self.tick_queue:
            q = self.tick_queue[contract]
            tk = await q.get()
            for callback in self.tick_queue_update[contract]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(tk)
                else:
                    callback(tk)


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
    async with aiohttp.ClientSession() as sess:
        from . import autil
        res, err = await autil.http_go(sess.get, f'https://api.1token.trade/v1/quote/single-tick/{contract}')
        if not err:
            res = Tick.from_dict(res)

        return res, err


async def subscribe_tick(contract, on_update):
    c = await get_client()
    return await c.subscribe_tick(contract, on_update)
