"""
async util
"""
import asyncio
import json
import logging
from datetime import datetime

import aiohttp
import arrow


def dumper(obj):
    if isinstance(obj, arrow.Arrow):
        return obj.isoformat()
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def make_key(args, kwargs) -> str:
    k = f'{args}{kwargs}'
    return k


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
