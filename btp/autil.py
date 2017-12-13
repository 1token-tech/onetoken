"""
async util
"""
import asyncio
import aiohttp
import functools
import json
import logging
from collections import defaultdict
from datetime import timedelta, datetime
from typing import Dict

import arrow
import asyncio_redis

from .model import Contract
from .logger import log


def throttle(t):
    """
    被这个wrapper 包裹的函数 每t秒最多 一次

    这个函数一般用的时候不关心参数 比如trade 最多几秒触发一次

    :param t:
    :return:
    """

    init = arrow.now() - timedelta(seconds=t)
    last = defaultdict(lambda: init)

    def wrapper(func):
        async def heihaa(*args, **kwargs):
            key = args[0]
            nonlocal last
            if arrow.now() - last[key] < timedelta(seconds=t):
                return
            last[key] = arrow.now()
            res = await func(*args, **kwargs)
            return res

        return heihaa

    return wrapper


def single_and_lock(func):
    """
    被wrap的函数只会被调用一次
    被wrap的函数只能是一个async函数
    被wrap的函数一定是一个class的function， 他的第一个self会被当成 key
    被wrap的函数没有返回
    :return:
    """
    lock = defaultdict(lambda: asyncio.Lock())
    finished = defaultdict(bool)

    async def wrap(*args, **kwargs):
        key = args[0]
        async with lock[key]:
            try:
                if finished[key]:
                    return
                await func(*args, **kwargs)
                finished[key] = True
            except:
                logging.exception('failed call')

    return wrap


class Cache:
    # data = {}
    #
    # @classmethod
    # async def call(cls, account, func):
    #     key = (account.symbol, func)
    #     if key not in cls.data:
    #         cls.data[key] = Cache(func)
    #     r = cls.data[key]
    #     return await r.get_result()

    def __init__(self, func, expire):
        logging.debug('new cache', func, expire)
        self.last_modified = None
        self.expire = timedelta(seconds=expire)
        # self.account = account
        self.func = func
        self.last_result = None
        self.lock = asyncio.Lock()

    async def get_result(self, *args, **kwargs):
        # from .logger import logger
        async with self.lock:
            if self.last_modified and arrow.now() < self.last_modified + self.expire:
                log.debug('cache hit', arrow.now(), self.last_modified)
                return self.last_result
            log.debug('cache miss', arrow.now(), self.last_modified)
            result = await self.func(*args, **kwargs)
            self.last_modified = arrow.now()
            self.last_result = result
            return result


_redis_conn = {}
_redis_conn_lock = asyncio.Lock()


def dumper(obj):
    if isinstance(obj, Contract):
        return obj.symbol
    if isinstance(obj, arrow.Arrow):
        return obj.isoformat()
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def make_key(args, kwargs) -> str:
    k = f'{args}{kwargs}'
    return k


def cache(expire=1):
    """
    这个函数一般被用的时候 是一个缓存 所以参数传入不同。 得到的结果是不同的。
    比如get_info 这就不需要参数。比如得到order info这就需要因素


    @cache_async(1)
    def gogo(self, para1):
        print('called')

    foo.gogo(1)
    foo.gogo(2) will call
    foo.gogo(1) will NOT call

    :param expire:
    :return:
    """
    expire = expire  # 三秒失效
    cache_map = {}  # type:Dict[str, Cache]

    def wrapper(f):
        assert asyncio.iscoroutinefunction(f)

        async def new(*args, **kwargs):
            key = make_key(args, kwargs)
            if key not in cache_map:
                cache_map[key] = Cache(f, expire)

            c = cache_map[key]
            return await c.get_result(*args, **kwargs)

        return new

    return wrapper


async def loop_call(func, wait, panic_on_fail=True):
    """
    :param func: 一个coroutine
    :param wait:
    :param panic_on_fail: True的话 func抛出异常就不行
    :return:
    """
    while True:
        try:
            await func()
        except:
            logging.exception('failed')
            # 良好的错误处理
            if panic_on_fail:
                from . import panic
                panic(f'loop call failed {func} {wait}')
        await asyncio.sleep(wait)


async def http(func, url, timeout=5, method='json', accept_4xx=True, *args, **kwargs):
    resp = await asyncio.wait_for(func(url, *args, **kwargs), timeout)
    txt = await resp.text()
    if not accept_4xx and resp.status != 200:
        raise ValueError('status {}'.format(resp.status), txt)
    # assert isinstance(resp, )
    if method == 'json':
        try:
            return json.loads(txt)
        except:
            raise ValueError('NOT_JSON', txt)
    elif method == 'text':
        return txt
    else:
        logging.warning('method {} not recognized'.format(method))
        assert False


async def http_go(func, url, timeout=15, method='json', accept_4xx=False, *args, **kwargs):
    """

    :param func:
    :param url:
    :param timeout:
    :param method:
        json -> return json dict
        raw -> return raw object
        text -> return string

    :param accept_4xx:
    :param args:
    :param kwargs:
    :return:
    """
    from . import HTTPError
    assert not accept_4xx
    assert method in ['json', 'text', 'raw']
    try:
        resp = await asyncio.wait_for(func(url, *args, **kwargs), timeout)
    except asyncio.TimeoutError:
        return None, HTTPError(HTTPError.TIMEOUT, "")
    except aiohttp.ClientError as e:
        return None, HTTPError(HTTPError.HTTP_ERROR, str(e))

    txt = await resp.text()

    if resp.status >= 500:
        return None, HTTPError(HTTPError.RESPONSE_5XX, txt)

    if 400 <= resp.status < 500:
        return None, HTTPError(HTTPError.RESPONSE_4XX, txt)

    if method == 'raw':
        return resp, None
    elif method == 'text':
        return txt, None
    elif method == 'json':
        try:
            return json.loads(txt), None
        except:
            return None, HTTPError(HTTPError.NOT_JSON, txt)


def must_finish(timeout=5):
    """
    example:
    @must_finish(5)
    async def connect():
        await ws_connect('www.slow.com')

    :param timeout:
    :return:
    """

    def decorator(async_func):
        async def wrapper(*args, **kwargs):
            coro = async_func(*args, **kwargs)
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                from . import panic
                panic('timeout {} {} {}'.format(async_func, args, kwargs))

        return wrapper

    return decorator


_async_redis_conn = None
