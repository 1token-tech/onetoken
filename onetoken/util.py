import random
import string
import arrow


def rand_id():
    # return uuid.uuid4()
    r = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
    r = r[5:]
    return r


def rand_client_oid(contract_symbol):
    """
        binance/xxx.yyy-yearmonthday-hourminuteseconds-random
    :param contract_symbol:
    :return:
    """
    now = arrow.now().format('YYYYMMDD-HHmmss')
    rand = rand_id()
    oid = f'{contract_symbol}-{now}-{rand}'
    return oid


def rand_client_wid(exchange, currency):
    """
    binance/xxx-yearmonthday-hourminuteseconds-random
    :param exchange:
    :param currency:
    :return:
    """
    now = arrow.now().format('YYYYMMDD-HHmmss')
    rand = rand_id()
    cwid = f'{exchange}/{currency}-{now}-{rand}'
    return cwid
