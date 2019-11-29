import json
import logging
import random
from typing import List

import arrow
import threading
import time
import gzip
import websocket
from websocket import ABNF

sz = 0
start = arrow.now()


class QuoteV2:
    def __init__(self, contract: List):
        self.ws_url = 'wss://1token.trade/api/v1/ws/tick'
        self.ws = None
        self.pong = 0
        self.contract = contract

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
        self.send_message(json.dumps(js))

    def heart_beat_loop(self):
        while self.ws and self.ws.keep_running:
            time.sleep(15)
            try:
                if time.time() - self.pong > 25:
                    logging.warning('connection heart beat lost')
                    break
                else:
                    self.send_json({'uri': 'ping'})
            except:
                logging.exception('failed')

    def on_data(self, msg, msg_type, *args):
        global sz
        sz += (len(msg))
        tm = (arrow.now() - start).total_seconds()
        if random.random() < 0.01:
            print(sz / tm / 1000, 'kb/s')
        try:
            if msg_type == ABNF.OPCODE_BINARY or msg_type == ABNF.OPCODE_TEXT:
                if msg_type == ABNF.OPCODE_TEXT:
                    data = json.loads(msg)
                else:
                    data = json.loads(gzip.decompress(msg).decode())
                uri = data.get('uri', 'data')
                if uri == 'pong':
                    self.pong = arrow.now().timestamp
                elif uri in ['auth']:
                    pass
                elif uri == 'single-tick-verbose':
                    self.handle(data)
                elif uri == 'subscribe-single-tick-verbose':
                    pass
                else:
                    print('unhandled', data)
        except Exception as e:
            logging.exception('failed', e)

    def on_open(self):
        self.pong = time.time()
        threading.Thread(target=self.heart_beat_loop).start()

        self.send_json({'uri': 'auth'})
        time.sleep(1)
        for c in self.contract:
            self.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': c})

    @staticmethod
    def on_error(ws, error):
        """
        websocket 发生错误的回调
        :param error:
        :return: None
        """
        print('on error')
        logging.exception(error)

    @staticmethod
    def on_close(*args):
        """
        websocket 关闭的回调
        :return: None
        """
        print("### websocket closed ###")

    def run(self) -> None:
        """
        运行 websocket
        :return: None
        """
        self.ws_connect()

    @staticmethod
    def handle(data):
        data = data['data']
        tm = data['time']
        contract = data['contract']
        bid1 = data['bids'][0]['price']
        ask1 = data['asks'][0]['price']
        last = data['last']
        print('%s | %-20s | %f/%f | %f' % (tm, contract, bid1, ask1, last))


def main():
    q = QuoteV2(contract=['okex/btc.usdt', 'binance/btc.usdt', 'huobip/btc.usdt'])
    q.run()


if __name__ == '__main__':
    main()
