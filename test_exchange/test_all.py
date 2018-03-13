import unittest
import asyncio
import onetoken as ot
from onetoken import Account, log
from .util import load_api_key_secret, input_api_key_secret
import time


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
            'con': cls.exchange + '/eth.usdt',
            'bs': 's',
            'price': 100000,
            'amount': 0.05
        }
        cls.order2 = {
            'con': cls.exchange + '/iost.usdt',
            'bs': 's',
            'price': 10000,
            'amount': 1.1
        }
        print('initializing account {}'.format(cls.account))
        time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        cls.acc.close()

    # @unittest.skip('get info')
    def test_get_info(self):
        info, err = self.loop.run_until_complete(self.acc.get_info())
        print(f'account info: {info.data}')
        print(f'err should be None: {err}')

        self.assertIsInstance(info, ot.Info)
        self.assertIsNone(err)

        #  AccountInfo至少包含法币(usdt)和btc
        real_currency = {'usdt', 'cny', 'jpy', 'usd', 'krw'}
        has_real_currency = False
        has_btc = False
        position = info.data['position']
        for pos in position:
            c = pos['contract']
            if c == 'btc':
                has_btc = True
            if c in real_currency:
                has_real_currency = True
        self.assertTrue(has_real_currency, 'real currency or usdt is not included')
        self.assertTrue(has_btc, 'btc is not included')

        # balance = cash + market_value(w.o. futures)
        self.assertEqual(info.data['balance'], info.data['cash'] + info.data['market_value'],
                         'balance != cash + market_value')

        for pos in position:
            self.assertEqual(pos['total_amount'], pos['available'] + pos['frozen'],
                             'position total_amount != available + frozen')
            if pos['contract'] == 'usdt':
                # usdt_price = self.loop.run_until_complete(otlib.autil.get_price('index/usdt.usd'))
                self.assertEqual(pos['market_value'], 0.0, 'usdt market_value != 0.0')
                # self.assertAlmostEqual(pos['value_cny'], pos['total_amount'] * qb.Currency.USDCNY * usdt_price,
                #                        delta=1e-8, msg='usdt value_cny is not correct')

    @unittest.skip('get order list')
    def test_get_order_list(self):
        pending_list, err = self.loop.run_until_complete(self.acc.get_order_list())
        print(f'pending list: {pending_list}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(pending_list, list)

    @unittest.skip('order')
    def test_order(self):
        self.place_order()
        self.cancel_order()
        self.get_order()

    def place_order(self):
        print(f'>>>start test place order')
        order1, err = self.loop.run_until_complete(self.acc.place_order(**self.order1))
        print(f'new order: {order1}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(order1, dict)
        self.exchange_oid = order1.get('exchange_oid', '')
        self.client_oid = order1.get('client_oid', '')
        self.assertRegex(self.exchange_oid, self.exchange + r'/[a-z]+\.[a-z]+-[\d]+')
        self.assertRegex(self.client_oid, self.exchange + r'/[a-z]+\.[a-z]+-[\d]+-[\d]+-[\w]+')
        order2, err = self.loop.run_until_complete(self.acc.place_order(**self.order2))
        print(f'new order should be None: {order2}')
        print(f'err should be HTTPError: {err}')
        self.assertIsNone(order2)
        self.assertIsNotNone(err)
        order_list, err = self.loop.run_until_complete(self.acc.get_order_list())
        self.assertIsNone(err)
        self.assertIsNotNone(order_list)

        exg_oid_in_pending_list = False
        for o in order_list:
            if o['exchange_oid'] == self.exchange_oid:
                exg_oid_in_pending_list = True
        self.assertTrue(exg_oid_in_pending_list, 'exchange_oid not in pending list')

        print(f'>>>end test place order')
        time.sleep(1)

    def get_order(self):
        print(f'>>>start test get order')
        order, err = self.loop.run_until_complete(self.acc.get_order_use_exchange_oid(self.exchange_oid))
        print(f'order: {order}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(order, list)
        self.assertEqual(len(order), 1)
        order = order[0]
        self.assertEqual(order['exchange_oid'], self.exchange_oid)
        self.assertEqual(order['client_oid'], self.client_oid)
        order, err = self.loop.run_until_complete(self.acc.get_order_use_client_oid(self.client_oid))
        print(f'order: {order}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(order, list)
        self.assertEqual(len(order), 1)
        order = order[0]
        self.assertEqual(order['exchange_oid'], self.exchange_oid)
        self.assertEqual(order['client_oid'], self.client_oid)
        print(f'>>>end test get order')
        time.sleep(1)

    def cancel_order(self):
        print(f'>>>start test cancel order')
        order, err = self.loop.run_until_complete(self.acc.cancel_use_exchange_oid(self.exchange_oid))
        print(f'order: {order}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(order, dict)
        self.assertEqual(order['exchange_oid'], self.exchange_oid)

        order_list, err = self.loop.run_until_complete(self.acc.get_order_list())
        self.assertIsNone(err)
        self.assertIsNotNone(order_list)

        exg_oid_in_pending_list = False
        for o in order_list:
            if o['exchange_oid'] == self.exchange_oid:
                exg_oid_in_pending_list = True
        self.assertFalse(exg_oid_in_pending_list, 'exchange_oid still in pending list')

        print(f'>>>end test cancel order')
        time.sleep(1)

    # @unittest.skip('cancel all')
    def test_cancel_all(self):
        print(f'>>>start test cancel all')
        res, err = self.loop.run_until_complete(self.acc.cancel_all())
        print(f'response: {res}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        time.sleep(1)

    @unittest.skip('skip')
    def test_withdraw(self):
        self.post_withdraw()
        self.cancel_withdraw()
        self.get_withdraw()

    @unittest.skip('not supported yet')
    def post_withdraw(self):
        print(f'>>>start test post withdraw')
        res, err = self.loop.run_until_complete(self.acc.post_withdraw(**self.withdraw))
        print(f'response: {res}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        self.assertRegex(res['exchange_wid'], self.exchange + '/' + self.withdraw['currency'] + r'-[\d]+')
        # self.assertRegex(res['client_wid'], self.exchange + '/' + self.withdraw['currency'] + r'-[\d]+-[\d]+-[\w]+')  # not implemented yet
        self.exchange_wid = res['exchange_wid']
        print(f'>>>end test post withdraw')
        time.sleep(1)

    @unittest.skip('not supported yet')
    def get_withdraw(self):
        print(f'>>>start test get withdraw')
        res, err = self.loop.run_until_complete(self.acc.get_withdraw_use_exchange_wid(self.exchange_wid))
        print(f'response: {res}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['exchange_wid'], self.exchange_wid)
        print('>>>end test get withdraw')
        time.sleep(1)

    @unittest.skip('not supported yet')
    def get_withdraw_list(self):
        time.sleep(1)

    @unittest.skip('not supported yet')
    def cancel_withdraw(self):
        print('>>>start test cancel withdraw')
        res, err = self.loop.run_until_complete(self.acc.cancel_withdraw_use_exchange_wid(self.exchange_wid))
        print(f'response: {res}')
        print(f'err should be None: {err}')
        self.assertIsNone(err)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['exchange_wid'], self.exchange_wid)
        print('>>>end test cancel withdraw')
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
