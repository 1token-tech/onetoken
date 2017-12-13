import asyncio
import json
import yaml
import os
import logging

try:
    import jwt
except:
    logging.warning('install pyjwt first')

import aiohttp

from . import Order
from . import OrderPool
from . import autil
from . import util
from . import log


class config:
    api_host = 'http://api.qbtrade.org'


def merge_slash(url):
    if url.startswith('http://'):
        begin = len('http://')
    elif url.startswith('https://'):
        begin = len('https://')
    else:
        begin = 0
    tail = url[begin:]
    while tail.find('//') >= 0:
        tail = tail.replace('//', '/')
    url = url[:begin] + tail
    return url


def use_trans_host(symbol):
    return False
    # if 'xtc.huobix' in symbol or 'xtc.jubi' in symbol or 'xtc.bitmex' in symbol:
    #     return True
    # else:
    #     return False


def get_trans_host(symbol, host):
    sp = symbol.split('@')
    if host is None:
        return config.api_host + f'/trans/{sp[1]}/{sp[0]}'
    else:
        return host + f'/{sp[1]}/{sp[0]}'


def gen_jwt(secret, uid):
    payload = {
        'user': uid,
        # 'nonce': nonce
    }
    c = jwt.encode(payload, secret, algorithm='RS256', headers={'iss': 'qb-trade', 'alg': 'RS256', 'typ': 'JWT'})
    return c.decode('ascii')


class Account:
    def __init__(self, symbol: str, subscribe_order_update=False, remove_finished_order=True, loop=None, host=None,
                 strategy=None, auth=True, no_strategy_warning=True):
        """

        :param symbol:
        :param subscribe_order_update:
        :param remove_finished_order:
        :param loop:
        :param host:
        """
        self.auth = auth
        if auth:
            path = os.path.expanduser('~/.qb/auth_config.yml')
            if not os.path.isfile(path):
                path = os.path.expanduser('~/.qb/auth_config.yaml')
                log.warning('please change suffix to *.yml')
            try:
                user_config = open(path).read()
                user_config = yaml.load(user_config)
            except Exception as e:
                log.exception('failed to read auth config...', e)
                raise Exception(f'failed to read auth config at {path}')
            try:
                self.user_name = user_config['user']
                self.secret = open(os.path.expanduser(user_config['secret_path'])).read()
            except Exception as e:
                log.exception('failed to get user id or secret...', e)
                assert False

        if strategy is None and no_strategy_warning:
            log.warning('set strategy will let others know this account is being used')
        else:
            # from . import autil
            # import functools
            # asyncio.ensure_future(autil.loop_call(functools.partial(register_strategy, symbol, strategy), 60))
            log.warning('strategy tag is not available yet。。')
        self.symbol = symbol
        # self.orders = {}
        self.order_pool = OrderPool(self)
        self.order_q = {}
        self.remove_finished_order = remove_finished_order

        if subscribe_order_update:
            log.warning('order subscribe is not available yet。。')
            # asyncio.ensure_future(self.subscribe_redis_order_update())
        log.debug('async account init {}'.format(symbol))
        self.session = aiohttp.ClientSession(loop=loop)
        if use_trans_host(symbol):
            self.host = get_trans_host(symbol, host)
            log.info(f'use host {self.host}')
        else:
            if host is None:
                self.host = config.api_host + '/trade/'
            else:
                self.host = host
            self.host += '/' + self.symbol
        self.host = merge_slash(self.host)
        log.debug('host', self.host)
        self.last_info = None
        self.conn = None
        self.closed = False

    def close(self):
        if self.conn:
            self.conn.close()
        self.session.close()
        self.closed = True

    def __del__(self):
        if self.session:
            self.session.close()

    def __str__(self):
        return '<{}>'.format(self.symbol)

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.symbol)

    async def get_pending_list(self):
        t = await self.api_call('get', '/orders')
        return t

    async def cancel_use_ref_key(self, ref_key):
        log.debug('cancel use ref_key', ref_key)

        # res = await autil.http(self.session.post, url=self.host + '/orders', data=data, timeout=15)
        data = {'ref_key': ref_key}
        # t = await autil.http(self.session.delete, url=self.host + '/orders/' + ref_key, timeout=15, data=data)
        t = await self.api_call('delete', '/orders/' + ref_key, data=data)
        return t

    async def cancel_use_entrust_no(self, entrust_no):
        log.debug('cancel use entrust_no', entrust_no)
        # t = await autil.http(self.session.delete, url=self.host + '/orders_entrust_no/' + entrust_no, timeout=15)
        t = await self.api_call('delete', '/orders_entrust_no/' + entrust_no)
        return t

    async def cancel_all(self):
        log.debug('cancel all')
        # t = await autil.http(self.session.delete, url=self.host + '/orders', timeout=15)
        t = await self.api_call('delete', '/orders')
        return t

    async def get_info(self, timeout=15):
        # y = await autil.http(self.session.get, url=self.host + '/info', timeout=timeout)
        y, err = await self.api_call('get', '/info', timeout=timeout)
        if err:
            return None, err
        if 'position' not in y:
            log.warning('failed', self.symbol, str(y))
            return None, Exception('ACC_GET_INFO_FAILED')
        y['position_dict'] = {item['contract']: item for item in y['position']}
        self.last_info = y
        return y, None

    def get_total_amount(self, con):
        if self.last_info is None:
            log.warning('no info')
        else:
            if con.symbol in self.last_info['position_dict']:
                return float(self.last_info['position_dict'][con.symbol]['total_amount'])
            else:
                log.warning('con {} not in position'.format(con.symbol))
                return 0.0

    async def place_and_cancel(self, con, price, bs, amount, sleep, options=None, on_trade=None, on_update=None):
        k = util.rand_ref_key()
        res1, err = await self.place_order(con, price, bs, amount,
                                           ref_key=k,
                                           options=options,
                                           on_trade=on_trade,
                                           on_update=on_update)
        await asyncio.sleep(sleep)
        res2, err = await self.cancel_use_ref_key(k)
        return [res1, res2], None

    async def get_health(self):
        return await self.api_call('get', '/health')

    async def amend_order(self, ref_key, price, amount):
        """
        :param price:
        :param amount:
        :param ref_key:
        :return:
        """
        log.debug('amend order', ref_key, price, amount)

        data = {'price': price,
                'amount': amount,
                'ref_key': ref_key}
        res = await self.api_call('put', f'/orders/{ref_key}', data=data)
        log.debug(res)
        return res

    async def place_order(self, con, price, bs, amount, ref_key=None, on_update=None, on_trade=None, tags=None,
                          options=None, **kwargs):
        """
        # call post api.qbtrade.org/trade/{acc}/orders
        just pass request, and handle order update --> fire callback and ref_key
        :param options:
        :param con:
        :param price:
        :param bs:
        :param amount:
        :param ref_key:
        :param tags: a key value dict
        :param on_update:
        :param on_trade: when something dealed, on_trade will be called
        :param kwargs: anything that will be passed to post
        :return:
        """
        log.debug('place order', con=con, price=price, bs=bs, amount=amount, ref_key=ref_key)

        if ref_key is None:
            ref_key = util.rand_ref_key()

        if on_update or on_trade:
            o = self.order_pool.fetch(ref_key, create=True)
            o.contract = con
            o.entrust_price = price
            o.bs = bs
            o.entrust_amount = amount
            o.ref_key = ref_key
            self.order_q[ref_key] = asyncio.Queue()
            asyncio.ensure_future(self.handle_q(ref_key, on_update, on_trade))
        data = {'contract': con,
                'price': price,
                'bs': bs,
                'amount': amount}
        if ref_key:
            data['ref_key'] = ref_key
        if tags:
            data['tags'] = ','.join(['{}:{}'.format(k, v) for k, v in tags.items()])
        if options:
            data['options'] = json.dumps(options)
            # data['options'] = ','.join(['{}:{}'.format(k, v) for k, v in options.items()])
        # res = await autil.http(self.session.post, url=self.host + '/orders', data=data, timeout=15)
        res = await self.api_call('post', '/orders', data=data)
        log.debug(res)
        return res

    @property
    def is_running(self):
        return not self.closed

    async def handle_q(self, ref_key, on_update, on_trade):
        """
        :param ref_key:
        :param on_update: callback
        :param on_trade: callback
        :return:
        """
        q = self.order_q[ref_key]
        last_dealed_amount = 0
        while True:
            try:
                order = await q.get()
                self.order_pool.pool[order.ref_key] = order
                log.debug('on update order {}'.format(order))
                if on_update is not None:
                    assert callable(on_update), 'on_update is not callable'
                    if asyncio.iscoroutinefunction(on_update):
                        await on_update(order)
                    else:
                        on_update(order)
                if on_trade is not None:
                    if order.dealed_amount > last_dealed_amount:
                        last_dealed_amount = order.dealed_amount
                        trans = order.dealed_trans[-1]
                        log.debug('dealed-trans {}'.format(trans.to_dict()))
                        if asyncio.iscoroutinefunction(on_trade):
                            await on_trade(trans)
                        else:
                            on_trade(trans)
                if order.status in Order.ENDING_STATUSES:
                    log.debug('{} finished with status {}'.format(order.ref_key[:4], order.status))
                    break
            except:
                log.exception('handle q failed')
        if self.remove_finished_order:
            # remove finished order in pool
            del self.order_pool.pool[ref_key]
            del self.order_q[ref_key]

    async def api_call(self, method, endpoint, params=None, data=None, timeout=15):
        method = method.lower()
        if method == 'get':
            func = self.session.get
        elif method == 'post':
            func = self.session.post
        elif method == 'put':
            func = self.session.put
        elif method == 'delete':
            func = self.session.delete
        else:
            raise Exception('invalid http method:{}'.format(method))

        if self.auth:
            headers = {'jwt': gen_jwt(self.secret, self.user_name)}
        else:
            headers = None

        url = self.host + endpoint
        res, err = await autil.http_go(func, url=url, data=data, params=params, headers=headers, timeout=timeout)
        if err:
            return None, err

        return res, None
