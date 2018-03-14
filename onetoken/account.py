import asyncio
import json
import urllib
import hmac
from typing import Union, Tuple

import aiohttp
import jwt
import time
import hashlib

from . import autil
from . import log
from . import util


class Config:
    api_host = 'https://api.1token.trade/v1/trade'


def get_trans_host(symbol):
    name, exg = get_name_exchange(symbol)
    return '/{}/{}'.format(exg, name)


def get_name_exchange(symbol):
    sp = symbol.split('/', 1)
    return sp[1], sp[0]


def gen_jwt(secret, uid):
    payload = {
        'user': uid,
        # 'nonce': nonce
    }
    c = jwt.encode(payload, secret, algorithm='RS256', headers={'iss': 'qb-trade', 'alg': 'RS256', 'typ': 'JWT'})
    return c.decode('ascii')


def gen_nonce():
    return str(int(time.time() * 1000000))


def gen_sign(secret, verb, url, nonce, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.

    if data is None:
        data_str = ''
    else:
        assert isinstance(data, dict)
        data_str = json.dumps(data, sort_keys=True)

    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path

    # print "Computing HMAC: %s" % verb + path + str(nonce) + data
    message = verb + path + str(nonce) + data_str
    # print(message)

    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature


class Info:
    def __init__(self, data):
        assert isinstance(data, dict)
        # if 'position' not in y:
        #     log.warning('failed', self.symbol, str(y))
        #     return None, Exception('ACC_GET_INFO_FAILED')
        self.data = data
        # ['position_dict']
        self.position_dict = {item['contract']: item for item in data.get('position', [])}

    @property
    def balance(self):
        return self.data['balance']

    def get_total_amount(self, pos_symbol):
        if pos_symbol in self.position_dict:
            return float(self.position_dict[pos_symbol]['total_amount'])
        else:
            return 0.0


class Account:
    def __init__(self, symbol: str, api_key, api_secret, loop=None):
        """

        :param symbol:
        :param api_key:
        :param api_secret:
        :param loop:
        """
        self.symbol = symbol
        self.api_key = api_key
        self.api_secret = api_secret
        log.debug('async account init {}'.format(symbol))
        self.session = None
        self.trans_path = get_trans_host(symbol)
        self.session = aiohttp.ClientSession(loop=loop)
        self.name, self.exchange = get_name_exchange(symbol)
        self.host = Config.api_host + self.trans_path
        log.debug('host', self.host)
        # self.last_info = None
        self.closed = False

    def close(self):
        if self.session and not self.session.closed:
            self.session.close()
        self.closed = True

    def __del__(self):
        self.close()

    def __str__(self):
        return '<{}>'.format(self.symbol)

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.symbol)

    async def get_pending_list(self):
        return await self.get_order_list()

    async def get_order_list(self, contract_name=None, state=None):
        data = {}
        if contract_name:
            data['contract_name'] = contract_name
        if state:
            data['state'] = state
        t = await self.api_call('get', '/orders', params=data)
        return t

    async def cancel_use_client_oid(self, oid):
        log.debug('Cancel use client oid', oid)

        data = {'client_oid': oid}
        t = await self.api_call('delete', '/orders', params=data)
        return t

    async def cancel_use_exchange_oid(self, oid):
        log.debug('Cancel use exchange oid', oid)
        data = {'exchange_oid': oid}
        t = await self.api_call('delete', '/orders', params=data)
        return t

    async def cancel_all(self):
        log.debug('Cancel all')
        t = await self.api_call('delete', '/orders/all')
        return t

    async def get_info(self, timeout=15) -> Tuple[Union[Info, None], Union[Exception, None]]:
        y, err = await self.api_call('get', '/info', timeout=timeout)
        if err:
            return None, err
        if not isinstance(y, dict):
            return None, ValueError(f'{y} not dict')
        return Info(y), None

    async def place_and_cancel(self, con, price, bs, amount, sleep, options=None):

        # k = util.rand_client_oid(con)
        k = util.rand_client_oid(con)
        res1, err1 = await self.place_order(con, price, bs, amount,
                                            client_oid=k,
                                            options=options)
        await asyncio.sleep(sleep)
        res2, err2 = await self.cancel_use_client_oid(k)
        if err1 or err2:
            return (res1, res2), (err1, err2)
        return [res1, res2], None

    async def get_status(self):
        return await self.api_call('get', '/status')

    async def get_order_use_client_oid(self, client_oid):
        """
        :param client_oid:
        :return:
        """
        res = await self.api_call('get', '/orders', params={'client_oid': client_oid})
        log.debug(res)
        return res

    async def get_order_use_exchange_oid(self, exchange_oid):
        """
        :param exchange_oid:
        :return:
        """
        res = await self.api_call('get', '/orders', params={'exchange_oid': exchange_oid})
        log.debug(res)
        return res

    async def amend_order_use_client_oid(self, client_oid, price, amount):
        """
        :param price:
        :param amount:
        :param client_oid:
        :return:
        """
        log.debug('Amend order use client oid', client_oid, price, amount)

        data = {'price': price,
                'amount': amount}
        params = {'client_oid': client_oid}
        res = await self.api_call('patch', '/orders', data=data, params=params)
        log.debug(res)
        return res

    async def amend_order_use_exchange_oid(self, exchange_oid, price, amount):
        """
        :param price:
        :param amount:
        :param exchange_oid:
        :return:
        """
        log.debug('Amend order use exchange oid', exchange_oid, price, amount)

        data = {'price': price,
                'amount': amount}
        params = {'exchange_oid': exchange_oid}
        res = await self.api_call('patch', '/orders', data=data, params=params)
        log.debug(res)
        return res

    async def place_order(self, con, price, bs, amount, client_oid=None, tags=None, options=None):
        """
        just pass request, and handle order update --> fire callback and ref_key
        :param options:
        :param con:
        :param price:
        :param bs:
        :param amount:
        :param client_oid:
        :param tags: a key value dict
        :return:
        """
        log.debug('Place order', con=con, price=price, bs=bs, amount=amount, client_oid=client_oid)

        if client_oid is None:
            client_oid = util.rand_client_oid(con)

        data = {'contract': con,
                'price': price,
                'bs': bs,
                'amount': amount}
        if client_oid:
            data['client_oid'] = client_oid
        if tags:
            data['tags'] = ','.join(['{}:{}'.format(k, v) for k, v in tags.items()])
        if options:
            data['options'] = json.dumps(options)
        res = await self.api_call('post', '/orders', data=data)
        log.debug(res)
        return res

    async def get_dealt_trans(self, con=None):
        """
        get recent dealt transactions
        :param con:
        :return:
        """
        log.debug('Get dealt trans', con=con)
        data = {}
        if con is not None:
            data['contract'] = con
        res = await self.api_call('get', '/trans', params=data)
        log.debug(res)
        return res

    async def post_withdraw(self, currency, amount, address, fee=None, client_wid=None, options=None):
        log.debug('Post withdraw', currency=currency, amount=amount, address=address, fee=fee, client_wid=client_wid)
        if client_wid is None:
            client_wid = util.rand_client_wid(self.exchange, currency)
        data = {
            'currency': currency,
            'amount': amount,
            'address': address
        }
        if fee is not None:
            data['fee'] = fee
        if client_wid:
            data['client_wid'] = client_wid
        if options:
            data['options'] = json.dumps(options)
        res = await self.api_call('post', '/withdraws', data=data)
        log.debug(res)
        return res

    async def cancel_withdraw_use_exchange_wid(self, exchange_wid):
        log.debug('Cancel withdraw use exchange_wid', exchange_wid)
        data = {'exchange_wid': exchange_wid}
        return await self.api_call('delete', '/withdraws', params=data)

    async def cancel_withdraw_use_client_wid(self, client_wid):
        log.debug('Cancel withdraw use client_wid', client_wid)
        data = {'client_wid': client_wid}
        return await self.api_call('delete', '/withdraws', params=data)

    async def get_withdraw_use_exchange_wid(self, exchange_wid):
        log.debug('Cancel withdraw use exchange_wid', exchange_wid)
        data = {'exchange_wid': exchange_wid}
        return await self.api_call('get', '/withdraws', params=data)

    async def get_withdraw_use_client_wid(self, client_wid):
        log.debug('Cancel withdraw use client_wid', client_wid)
        data = {'client_wid': client_wid}
        return await self.api_call('get', '/withdraws', params=data)

    @property
    def is_running(self):
        return not self.closed

    async def api_call(self, method, endpoint, params=None, data=None, timeout=15):
        method = method.upper()
        if method == 'GET':
            func = self.session.get
        elif method == 'POST':
            func = self.session.post
        elif method == 'PATCH':
            func = self.session.patch
        elif method == 'DELETE':
            func = self.session.delete
        else:
            raise Exception('Invalid http method:{}'.format(method))

        nonce = gen_nonce()
        # headers = {'jwt': gen_jwt(self.secret, self.user_name)}

        url = self.host + endpoint

        # print(self.api_secret, method, url, nonce, data)
        sign = gen_sign(self.api_secret, method, '/{}/{}{}'.format(self.exchange, self.name, endpoint), nonce, data)
        headers = {'Api-Nonce': str(nonce), 'Api-Key': self.api_key, 'Api-Signature': sign,
                   'Content-Type': 'application/json'}
        res, err = await autil.http_go(func, url=url, json=data, params=params, headers=headers, timeout=timeout)
        if err:
            return None, err
        return res, None
