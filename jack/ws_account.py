import gzip
import hashlib
import hmac
import json
import logging
import threading
import time

import websocket
from websocket import ABNF


class AccountWs:
    def __init__(self, symbol: str = None, api_key: str = None, api_secret: str = None):
        """

        :param symbol: exchange/account
        :param api_key: str
        :param api_secret: str
        """
        self.ws = None
        self.pong = 0
        self.symbol = symbol
        self.exchange, self.account = symbol.split('/', 1)
        self.host_ws = 'wss://cdn.1tokentrade.cn/api/v1/ws/trade/{}/{}'.format(self.exchange, self.account)
        self.api_key = api_key
        self.api_secret = api_secret
        self.sub_key = set()
        self.handle_info = None
        self.handle_order = None

    @staticmethod
    def gen_sign(secret, verb, path, nonce, data_str):
        """
        签名方法
        :param secret:
        :param verb:
        :param path:
        :param nonce:
        :param data_str:
        :return:
        """
        message = verb + path + str(nonce) + data_str
        print('sign message', message)
        signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def ws_connect(self):
        print('Connecting to {}'.format(self.host_ws))
        nonce = str(int(time.time() * 1000000))
        sign = self.gen_sign(self.api_secret, 'GET', path='/ws/' + self.account, nonce=nonce, data_str='')
        headers = {'Api-Nonce': str(nonce), 'Api-Key': self.api_key, 'Api-Signature': sign}
        self.ws = websocket.WebSocketApp(self.host_ws,
                                         header=headers,
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
            try:
                if time.time() - self.pong > 25:
                    logging.warning('connection heart beat lost')
                    break
                else:
                    ping = time.time()
                    self.send_json({'uri': 'ping', 'uuid': ping})
            except:
                logging.exception('unexpected failed')
            time.sleep(10)

    def on_data(self, msg, msg_type, *args):
        try:
            if msg_type == ABNF.OPCODE_BINARY or msg_type == ABNF.OPCODE_TEXT:
                if msg_type == ABNF.OPCODE_TEXT:
                    data = json.loads(msg)
                else:
                    data = json.loads(gzip.decompress(msg).decode())
                uri = data.get('uri')
                if uri == 'pong':
                    self.pong = time.time()
                elif uri in ['connection', 'status']:
                    if data.get('code', data.get('status', None)) in ['ok', 'connected']:
                        for key in self.sub_key:
                            self.send_json({'uri': 'sub-{}'.format(key)})
                elif uri == 'info':
                    if data.get('status', 'ok') == 'ok':
                        info = data['data']
                        self.handle_info(info)
                elif uri == 'order':
                    if data.get('status', 'ok') == 'ok':
                        for order in data['data']:
                            self.handle_order(order)
                elif uri in ['sub-order', 'sub-info']:
                    print(data['uri'], data['code'])
                else:
                    print('unhandled', data)
        except:
            logging.exception('unexpected failed')

    def on_open(self):
        print('connected on open')
        self.pong = time.time()
        threading.Thread(target=self.heart_beat_loop).start()

    @staticmethod
    def on_error(ws, error):
        """
        websocket 发生错误的回调
        :param error:
        :return: None
        """
        print('on error', error)
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

    def sub_info(self, callback=None):
        def _handle_info(data):
            print('on info update', data)

        self.sub_key.add('info')
        self.handle_info = callback if callback else _handle_info

    def sub_order(self, callback=None):
        def _handle_order(data):
            print('on order update', data)

        self.sub_key.add('order')
        self.handle_order = callback if callback else _handle_order


def main():
    acc_ws = AccountWs(symbol='okex/mock-jack', api_key='QCsKNH71-n8AqFBer-ZUdnRnKA-y1jsbYhU', api_secret='s53cGW3W-sdEXvOSA-i8JX9oAz-16mMA4sb')
    acc_ws.sub_info()
    acc_ws.sub_order()
    acc_ws.run()


if __name__ == '__main__':
    main()
