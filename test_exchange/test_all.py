import unittest
import asyncio
import onetoken as ot
from onetoken import Account, log
from .util import load_api_key_secret, input_api_key_secret
import time
import qbtrade as qb
import otlib


class TestExchanges(unittest.TestCase):
    CONFIG_FILE_PATH = '~/.onetoken/config.yml'
    api_key = None
    api_secret = None
    acc = None
    withdraw = {
        'currency': 'iost',
        'amount': 1.1,
        'address': ''
    }

    @classmethod
    def setUpClass(cls):
        cls.api_key, cls.api_secret, cls.account = load_api_key_secret(cls.CONFIG_FILE_PATH)
        if cls.api_key is None or cls.api_secret is None:
            cls.api_key, cls.api_secret, cls.account = input_api_key_secret()
        cls.acc = Account(cls.account, api_key=cls.api_key, api_secret=cls.api_secret)
        cls.loop = asyncio.get_event_loop()
        cls.exchange, cls.name = cls.account.split('/', 1)
        cls.order1 = {
            'con': cls.exchange + '/qtum.usdt',
            'bs': 's',
            'price': 10000,
            'amount': 1.1
        }
        cls.order2 = {
            'con': cls.exchange + '/iost.usdt',
            'bs': 's',
            'price': 10000,
            'amount': 1.1
        }
        log.info('initializing account {}'.format(cls.account))
        time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        cls.acc.close()

    @unittest.skip('skip usdt bug')
    def test_get_info(self):
        info, err = self.loop.run_until_complete(self.acc.get_info())
        log.info(f'account info: {info.data}')
        self.assertIsInstance(info, ot.Info)
        self.assertIsNone(err)
        position = info.data['position']
        for pos in position:
            self.assertEqual(pos['total_amount'], pos['available'] + pos['frozen'])
            if pos['contract'] == 'usdt':
                usdt_price = self.loop.run_until_complete(otlib.autil.get_price('index/usdt.usd'))
                self.assertEqual(pos['market_value'], 0.0)
                self.assertAlmostEqual(pos['value_cny'], pos['total_amount'] * qb.Currency.USDCNY * usdt_price,
                                       delta=1e-8)

    def test_get_pending_list(self):
        pending_list, err = self.loop.run_until_complete(self.acc.get_pending_list())
        log.info(f'pending list: {pending_list}')
        self.assertIsNone(err)
        self.assertIsInstance(pending_list, list)

    def test_order(self):
        self.place_order()
        self.cancel_order()
        self.get_order()

    def place_order(self):
        log.info(f'test place order')
        order1, err = self.loop.run_until_complete(self.acc.place_order(**self.order1))
        log.info(f'new order: {order1}')
        log.info(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(order1, dict)
        self.exchange_oid = order1.get('exchange_oid', '')
        self.client_oid = order1.get('client_oid', '')
        self.assertRegex(self.exchange_oid, self.exchange + r'/[a-z]+\.[a-z]+-[\d]+')
        self.assertRegex(self.client_oid, self.exchange + r'/[a-z]+\.[a-z]+-[\d]+-[\d]+-[\w]+')
        order2, err = self.loop.run_until_complete(self.acc.place_order(**self.order2))
        log.info(f'new order should be None: {order2}')
        log.info(f'err should be HTTPError: {err}')
        self.assertIsNone(order2)
        self.assertIsNotNone(err)
        log.info(f'end test place order')
        time.sleep(1)

    def get_order(self):
        log.info(f'test get order')
        order, err = self.loop.run_until_complete(self.acc.get_order_use_exchange_oid(self.exchange_oid))
        self.assertIsNone(err)
        self.assertIsInstance(order, list)
        self.assertEqual(len(order), 1)
        order = order[0]
        self.assertEqual(order['exchange_oid'], self.exchange_oid)
        self.assertEqual(order['client_oid'], self.client_oid)
        order, err = self.loop.run_until_complete(self.acc.get_order_use_client_oid(self.client_oid))
        self.assertIsNone(err)
        self.assertIsInstance(order, list)
        self.assertEqual(len(order), 1)
        order = order[0]
        self.assertEqual(order['exchange_oid'], self.exchange_oid)
        self.assertEqual(order['client_oid'], self.client_oid)
        log.info(f'end test get order')
        time.sleep(1)

    def cancel_order(self):
        log.info(f'test cancel order')
        order, err = self.loop.run_until_complete(self.acc.cancel_use_exchange_oid(self.exchange_oid))
        self.assertIsNone(err)
        self.assertIsInstance(order, dict)
        self.assertEqual(order['exchange_oid'], self.exchange_oid)
        log.info(f'end test cancel order')
        time.sleep(1)

    @unittest.skip('skip')
    def test_cancel_all(self):
        log.info(f'test cancel all')
        res, err = self.loop.run_until_complete(self.acc.cancel_all())
        log.info(f'response: {res}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        time.sleep(1)

    @unittest.skip('skip')
    def test_withdraw(self):
        self.post_withdraw()
        self.cancel_withdraw()
        self.get_withdraw()

    def post_withdraw(self):
        log.info(f'test post withdraw')
        res, err = self.loop.run_until_complete(self.acc.post_withdraw(**self.withdraw))
        log.info(f'response: {res}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        self.assertRegex(res['exchange_wid'], self.exchange + '/' + self.withdraw['currency'] + r'-[\d]+')
        # self.assertRegex(res['client_wid'], self.exchange + '/' + self.withdraw['currency'] + r'-[\d]+-[\w]+')  # not implemented yet
        self.exchange_wid = res['exchange_wid']
        log.info(f'end test post withdraw')
        time.sleep(1)

    def get_withdraw(self):
        log.info(f'test get withdraw')
        res, err = self.loop.run_until_complete(self.acc.get_withdraw_use_exchange_wid(self.exchange_wid))
        log.info(f'response: {res}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['exchange_wid'], self.exchange_wid)
        log.info('end test get withdraw')
        time.sleep(1)

    @unittest.skip('not supported yet')
    def get_withdraw_list(self):
        time.sleep(1)

    def cancel_withdraw(self):
        log.info('test cancel withdraw')
        res, err = self.loop.run_until_complete(self.acc.cancel_withdraw_use_exchange_wid(self.exchange_wid))
        log.info(f'response: {res}, err: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['exchange_wid'], self.exchange_wid)
        log.info('test cancel withdraw')
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
