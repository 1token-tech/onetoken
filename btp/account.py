import asyncio
import json
import os

import aiohttp
import jwt
import yaml

from . import autil
from . import log
from . import util


class Config:
    api_host = 'http://alihk-debug.qbtrade.org:3019/trade'


def get_trans_host(symbol, host):
    sp = symbol.split('@')
    if host is None:
        return Config.api_host + '/{}/{}'.format(sp[1], sp[0])
    else:
        return host + '/{}/{}'.format(sp[1], sp[0])


def gen_jwt(secret, uid):
    payload = {
        'user': uid,
        # 'nonce': nonce
    }
    c = jwt.encode(payload, secret, algorithm='RS256', headers={'iss': 'qb-trade', 'alg': 'RS256', 'typ': 'JWT'})
    return c.decode('ascii')


class Account:
    def __init__(self, symbol: str, loop=None, host=None):
        """

        :param symbol:
        :param loop:
        :param host:
        """
        path = os.path.expanduser('~/.qb/auth_config.yml')
        if not os.path.isfile(path):
            log.warning('~/.qb/auth_config.yml not exist')
        try:
            user_config = open(path).read()
            user_config = yaml.load(user_config)
        except Exception as e:
            log.exception('failed to read auth config...', e)
            raise Exception('failed to read auth config at {}'.format(path))
        try:
            self.user_name = user_config['user']
            self.secret = open(os.path.expanduser(user_config['secret_path'])).read()
        except Exception as e:
            log.exception('failed to get user id or secret...', e)
            assert False

        self.symbol = symbol

        log.debug('async account init {}'.format(symbol))
        self.session = aiohttp.ClientSession(loop=loop)
        self.host = get_trans_host(symbol, host)
        log.debug('host', self.host)
        self.last_info = None
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
        t = await self.api_call('get', '/orders')
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

    async def get_info(self, timeout=15):
        y, err = await self.api_call('get', '/info', timeout=timeout)
        if err:
            return None, err
        if 'position' not in y:
            log.warning('failed', self.symbol, str(y))
            return None, Exception('ACC_GET_INFO_FAILED')
        y['position_dict'] = {item['contract']: item for item in y['position']}
        self.last_info = y
        return y, None

    def get_total_amount(self, pos_symbol):
        if self.last_info is None:
            log.warning('no info')
        else:
            if pos_symbol in self.last_info['position_dict']:
                return float(self.last_info['position_dict'][pos_symbol]['total_amount'])
            else:
                log.warning('symbol {} not in position'.format(pos_symbol))
                return 0.0

    async def place_and_cancel(self, con, price, bs, amount, sleep, options=None):
        k = util.rand_ref_key()
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
            client_oid = util.rand_ref_key()

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

    @property
    def is_running(self):
        return not self.closed

    async def api_call(self, method, endpoint, params=None, data=None, timeout=15):
        method = method.lower()
        if method == 'get':
            func = self.session.get
        elif method == 'post':
            func = self.session.post
        elif method == 'patch':
            func = self.session.patch
        elif method == 'delete':
            func = self.session.delete
        else:
            raise Exception('Invalid http method:{}'.format(method))

        headers = {'jwt': gen_jwt(self.secret, self.user_name)}

        url = self.host + endpoint
        res, err = await autil.http_go(func, url=url, json=data, params=params, headers=headers, timeout=timeout)
        if err:
            return None, err
        return res, None
