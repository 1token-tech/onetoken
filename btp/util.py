import time
import random
import string
import logging
from datetime import timedelta, tzinfo, datetime


class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return timedelta(0)


gmtp0 = FixedOffset(0 * 60, "GMT+0")
gmtp3 = FixedOffset(3 * 60, "GMT+3")
gmtp8 = FixedOffset(8 * 60, "GMT+8")


def gmtp8now():
    return datetime.now(tz=gmtp8)


def rand_ref_key():
    # return uuid.uuid4()
    r = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
    r = '{}-{}'.format(r[:4], r[5:])
    assert len(r) == 32
    return r


def http_try(func, retries=3, timeout=5, method='json', **kwargs):
    """

    :param func:
    :param retries: 如果等于0的话。 一次都不重试。 如果等于1的话 会重试一次(最多发送两次请求)
    :param timeout:
    :param method:
    :param kwargs:
    :return:
    """

    import requests
    for reqexp_count in range(retries + 1):
        try:
            r = func(timeout=timeout, **kwargs)
            if method == 'json':
                try:
                    return r.json()
                except:
                    logging.warning("error parse json", kwargs, r.status_code, r.text[:500])
                    raise ValueError('parse json not success')
            else:
                return r.text
        except requests.RequestException:
            timeout *= 2
            params = str(kwargs.get('params', ''))[:400]
            logging.warning('http try wrong, retry after {}s {} {}'.format(timeout, kwargs['url'], params))
            if reqexp_count == retries:
                break
            # 最后一次就不用重试了
            time.sleep(timeout)
    raise Exception('network error')
