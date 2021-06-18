import _thread as thread
import json
import logging
import queue
import time
from collections import defaultdict

import arrow
import websocket
from websocket import ABNF


class Quote:
    def __init__(self, key, ws_url, data_parser):
        self.key = key
        self.ws_url = ws_url
        self.data_parser = data_parser
        self.ws = None
        self.queue_handlers = defaultdict(list)
        self.data_queue = {}
        self.authorized = False
        self.lock = thread.allocate_lock()
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
                    print(data)
                    self.authorized = True
                elif uri == 'subscribe-single-tick-verbose':
                    print(data)
                elif uri == 'subscribe-single-zhubi-verbose':
                    print(data)
                elif uri == 'subscribe-single-candle' and data.get('code'):
                    print(data)
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
    def on_error(error, msg):
        """
        websocket 发生错误的回调
        :param error:
        :return: None
        """
        print('on error', error, msg)

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


class CandleQuote(Quote):
    def __init__(self):
        super().__init__('candle', 'wss://1token.trade/api/v1/ws/candle', self.parse_candle)
        self.channel = 'subscribe-single-candle'

    def parse_candle(self, data):
        try:

            amount = data['amount']
            close = data['close']
            high = data['high']
            low = data['low']
            open = data['open']
            volume = data['volume']
            contract = data['contract']
            duration = data['duration']
            time = arrow.get(data['time'])

            q_key = json.dumps({'contract': contract, 'duration': duration, 'uri': self.channel}, sort_keys=True)

            candle = Candle(amount=amount, close=close, high=high, low=low, open=open, volume=volume,
                            contract=contract, duration=duration, time=time)
            return q_key, candle
        except Exception as e:
            print('fail', data, e, type(e))
            logging.exception('parse error')
        return None, None

    def subscribe_candle(self, contract, duration, on_update):
        assert duration in {'1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '1d', '1w'}

        self.subscribe_data(self.channel, on_update=on_update, contract=contract, duration=duration)


class Candle:
    def __init__(self, amount, close, high, low, open, volume, contract, duration, time):
        # internally use python3's datetime
        if isinstance(time, arrow.Arrow):
            time = time.datetime
        assert time.tzinfo
        self.amount = amount
        self.close = close
        self.high = high
        self.low = low
        self.open = open
        self.volume = volume
        self.contract = contract
        self.duration = duration
        self.time = time

    def __str__(self):
        return '<{} {} {} {} {} {} {} {} {}.{:03d}>'.format(self.amount,
                                                            self.close,
                                                            self.high,
                                                            self.low,
                                                            self.open,
                                                            self.volume,
                                                            self.contract,
                                                            self.duration,
                                                            self.time.strftime('%H:%M:%S'),
                                                            self.time.microsecond // 1000, )

    def __repr__(self):
        return str(self)


class Config:
    print_only_delay = False


def on_update(candle: Candle):
    delay = (arrow.now() - candle.time).total_seconds()
    print(arrow.now(), 'candle come 1', delay, candle)


def main_single():
    """
    订阅一个交易对
    :return:
    """
    candle = CandleQuote()
    candle.run()
    sub_list = [('binance/btc.usdt', '1m')]
    for contract, duration in sub_list:
        candle.subscribe_candle(contract, duration, on_update)

    time.sleep(100)
    candle.close()


if __name__ == '__main__':
    main_single()
