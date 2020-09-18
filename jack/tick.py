"""
Usage:
    tick.py [options]

Options:

"""
import _thread as thread
import json
import logging
from collections import defaultdict

import arrow
import queue
import time
import websocket
from websocket import ABNF


# 为一个Websocket多包一层
class Quote:
    def __init__(self, key, ws_url, data_parser):
        # name
        self.key = key
        self.ws_url = ws_url
        self.data_parser = data_parser
        self.ws = None
        self.queue_handlers = defaultdict(list)
        self.data_queue = {}
        self.authorized = False
        self.lock = thread.allocate_lock()
        # for heartbeat
        self.pong = 0
        self.is_running = False

    def ws_connect(self):
        print('Connecting to {}'.format(self.ws_url))
        self.ws = websocket.WebSocketApp(self.ws_url,
                                         on_open=self.on_open,
                                         on_data=self.on_data,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def send_message(self, message):
        """
        通过 websocket 发送消息
        :param message: string
        :return: None
        """
        self.ws.send(message)

    def send_json(self, js):
        """
        通过 websocket 发送json
        :param js: dict
        :return: None
        """
        self.ws.send(json.dumps(js))

    def heart_beat_loop(self):
        def run():
            while self.ws and self.ws.keep_running:
                try:
                    if time.time() - self.pong > 20:
                        print('connection heart beat lost')
                        self.ws.close()
                        break
                    else:
                        self.send_json({'uri': 'ping'})
                finally:
                    time.sleep(5)

        thread.start_new_thread(run, ())

    def on_data(self, msg, msg_type, *args):
        try:
            if msg_type == ABNF.OPCODE_BINARY or msg_type == ABNF.OPCODE_TEXT:
                import gzip
                if msg_type == ABNF.OPCODE_TEXT:
                    data = json.loads(msg)
                else:
                    data = json.loads(gzip.decompress(msg).decode())
                uri = data.get('uri', 'data')
                if uri == 'pong':
                    self.pong = arrow.now().timestamp
                elif uri == 'auth':
                    print('auth', data)
                    self.authorized = True
                elif uri == 'subscribe-single-tick-verbose':
                    print('subscribe-single-tick-verbose', data)
                elif uri == 'subscribe-single-zhubi-verbose':
                    print('subscribe-single-zhubi-verbose', data)
                elif uri == 'subscribe-single-candle':
                    print('subscribe-single-candle',data)
                else:
                    q_key, parsed_data = self.data_parser(data)
                    if q_key is None:
                        print('unknown message', data)
                        return
                    if q_key in self.data_queue:
                        self.data_queue[q_key].put(parsed_data)
        except Exception as e:
            print('msg error...', e)

    def on_open(self):
        print('on open')

        def run():
            self.pong = time.time()
            self.heart_beat_loop()
            self.send_json({'uri': 'auth'})
            wait_for_auth = time.time()
            while not self.authorized and time.time() - wait_for_auth < 5:
                time.sleep(0.1)
            if not self.authorized:
                print('wait for auth success timeout')
                self.ws.close()
            q_keys = list(self.queue_handlers.keys())
            if q_keys:
                print('recover subscriptions', q_keys)
                for q_key in q_keys:
                    sub_data = json.loads(q_key)
                    self.subscribe_data(**sub_data)
                    print(sub_data)

        thread.start_new_thread(run, ())

    @staticmethod
    def on_error(error):
        """
        websocket 发生错误的回调
        :param error:
        :return: None
        """
        print('on error', error)

    def on_close(self):
        """
        websocket 关闭的回调
        :return: None
        """
        print('on close')
        self.authorized = False
        print("### websocket closed ###")

    def subscribe_data(self, uri, on_update=None, **kwargs):
        print('subscribe', uri, kwargs)
        while not self.ws or not self.ws.keep_running or not self.authorized:
            time.sleep(1)
        sub_data = {'uri': uri}
        sub_data.update(kwargs)
        q_key = json.dumps(sub_data, sort_keys=True)
        with self.lock:
            try:
                self.send_json(sub_data)
                print('sub data', sub_data)
                if q_key not in self.data_queue:
                    self.data_queue[q_key] = queue.Queue()
                    if on_update:
                        if not self.queue_handlers[q_key]:
                            self.handle_q(q_key)
            except Exception as e:
                print('subscribe {} failed...'.format(kwargs))
            else:
                if on_update:
                    self.queue_handlers[q_key].append(on_update)

    def handle_q(self, q_key):
        def run():
            while q_key in self.data_queue:
                q = self.data_queue[q_key]
                try:
                    tk = q.get()
                except:
                    print('get data from queue failed')
                    continue
                for callback in self.queue_handlers[q_key]:
                    try:
                        callback(tk)
                    except:
                        logging.exception('quote callback fail')

        thread.start_new_thread(run, ())

    def run(self) -> None:
        """
        运行 websocket
        :return: None
        """

        def _run():
            while self.is_running:
                self.ws_connect()

        if self.is_running:
            print('ws is already running')
        else:
            self.is_running = True
            thread.start_new_thread(_run, ())

    def close(self):
        """
        关闭 websocket
        :return: None
        """
        self.is_running = False
        self.ws.close()
        self.ws = None  # type: (websocket.WebSocketApp, None)
        self.pong = 0
        self.queue_handlers = defaultdict(list)
        self.data_queue = {}
        self.authorized = False


# 在Quote层级多一级TickV3
class TickV3Quote(Quote):
    def __init__(self):
        super().__init__('tick.v3', 'wss://cdn.1tokentrade.cn/api/v1/ws/tick-v3?gzip=true', self.parse_tick)
        self.channel = 'subscribe-single-tick-verbose'
        self.ticks = {}

    def parse_tick(self, data):
        try:
            c = data['c']
            tm = arrow.get(data['tm'])
            et = arrow.get(data['et']) if 'et' in data else None
            tp = data['tp']
            q_key = json.dumps({'contract': c, 'uri': self.channel}, sort_keys=True)
            if tp == 's':
                bids = [{'price': p, 'volume': v} for p, v in data['b']]
                asks = [{'price': p, 'volume': v} for p, v in data['a']]
                tick = Tick(tm, data['l'], data['v'], bids, asks, c, 'tick.v3', et, data['vc'])
                self.ticks[tick.contract] = tick
                return q_key, tick
            elif tp == 'd':
                if c not in self.ticks:
                    print('update arriving before snapshot' + str(self.channel) + str(data))
                    return None, None
                tick = self.ticks[c].copy()

                tick.time = tm.datetime
                tick.exchange_time = et.datetime
                tick.price = data['l']
                tick.volume = data['v']
                tick.amount = data['vc']
                bids = {p: v for p, v in data['b']}
                old_bids = {item['price']: item['volume'] for item in tick.bids}
                old_bids.update(bids)
                bids = [{'price': p, 'volume': v} for p, v in old_bids.items() if v > 0]
                bids = sorted(bids, key=lambda x: x['price'], reverse=True)

                asks = {p: v for p, v in data['a']}
                old_asks = {item['price']: item['volume'] for item in tick.asks}
                old_asks.update(asks)
                asks = [{'price': p, 'volume': v} for p, v in old_asks.items() if v > 0]
                asks = sorted(asks, key=lambda x: x['price'])

                tick.bids = bids
                tick.asks = asks
                self.ticks[c] = tick
                return q_key, tick
        except Exception as e:
            print('fail', data, e, type(e))
            logging.exception('parse error')
        return None, None

    def subscribe_tick_v3(self, contract, on_update):
        self.subscribe_data(self.channel, on_update=on_update, contract=contract)


# 存放Tick的数据结构
class Tick:
    def copy(self):
        return Tick(time=self.time,
                    price=self.price,
                    volume=self.volume,
                    bids=json.loads(json.dumps(self.bids)),
                    asks=json.loads(json.dumps(self.asks)),
                    contract=self.contract,
                    source=self.source,
                    exchange_time=self.exchange_time,
                    amount=self.amount,
                    )

    def __init__(self, time, price, volume=0, bids=None, asks=None, contract=None,
                 source=None, exchange_time=None, amount=None, **kwargs):

        # internally use python3's datetime
        if isinstance(time, arrow.Arrow):
            time = time.datetime
        assert time.tzinfo
        self.contract = contract
        self.source = source
        self.time = time
        self.price = price
        self.volume = volume
        self.amount = amount
        self.bids = []
        self.asks = []
        if isinstance(time, arrow.Arrow):
            exchange_time = exchange_time.datetime
        if exchange_time:
            assert exchange_time.tzinfo
        self.exchange_time = exchange_time
        if bids:
            self.bids = sorted(bids, key=lambda x: -x['price'])
        if asks:
            self.asks = sorted(asks, key=lambda x: x['price'])
        for item in self.bids:
            assert 'price' in item and 'volume' in item
        for item in self.asks:
            assert 'price' in item and 'volume' in item
            # self.asks = asks

    # last as an candidate of last
    @property
    def last(self):
        return self.price

    @last.setter
    def last(self, value):
        self.price = value

    @property
    def bid1(self):
        if self.bids:
            return self.bids[0]['price']
        return None

    @property
    def ask1(self):
        if self.asks:
            return self.asks[0]['price']
        return None

    def __str__(self):
        return '<{} {}.{:03d} {}/{} {} {}>'.format(self.contract,
                                                   self.time.strftime('%H:%M:%S'),
                                                   self.time.microsecond // 1000,
                                                   self.bid1,
                                                   self.ask1,
                                                   self.last,
                                                   self.volume)

    def __repr__(self):
        return str(self)


class Config:
    print_only_delay = False


def on_update(tk: Tick):
    delay = (arrow.now() - tk.time).total_seconds()
    # print(tk)
    if tk.bid1 and tk.ask1:
        if tk.bid1 >= tk.ask1:
            print('bid1 >= ask1 %s %s', tk.bid1, tk.ask1)
    if delay > 10:
        print('tick delay comes', arrow.now(), 'tick come 1', delay, tk)




def get_tick():
    """
    订阅一个交易对
    :return:
    """
    tick_v3 = TickV3Quote()
    tick_v3.run()
    sub_list = ['binance/btc.usdt']
    for contract in sub_list:
        tick_v3.subscribe_tick_v3(contract, on_update)

    time.sleep(20)
    tick_v3.close()


if __name__ == '__main__':
    get_tick()
