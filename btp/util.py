import random
import string
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
