import json
import logging
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime
from functools import lru_cache, partial
from typing import Dict
from typing import List

import arrow
import dateutil
import dateutil.parser
import pandas as pd
import requests
import yaml

from . import util


class Model:
    def serialize(self, protocol):
        return protocol.dumps(self)


class ContractCategory:
    FUND = 'FUND'
    STOCK = 'STOCK'
    INDEX = 'INDEX'
    FUTURE = 'FUTURE'
    OPTION = 'OPTION'
    BOND = 'BOND'
    NAV = 'NAV'
    ESTIMATION = 'ESTIMATION'

    types = [FUND, STOCK, INDEX, FUTURE, OPTION, BOND]


class SymbolCompare:
    @property
    def symbol(self):
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __ne__(self, other):
        return not self.__eq__(other)


class Exchange(SymbolCompare):
    """
    a contract should be in and only in one exchange
    """

    def __init__(self, realm, name, uid=None, symbol=None):
        self.realm = realm
        self.name = name
        self.uid = uid
        self.given_symbol = symbol

    @property
    def symbol(self):
        """
        :return: a unique symbol accrossing all world
        """
        if self.given_symbol:
            return self.given_symbol
        return 'exchange.{}.{}'.format(self.realm, self.name)

    @classmethod
    def from_rest_dict(cls, dct):
        return cls(name=dct['name'], realm=dct['realm'], uid=dct['id'], symbol=dct['symbol'])
        # return cls(dct['realm'], dct['name'])

    @classmethod
    def from_mongo_dict(cls, dct):
        return Exchange(dct['realm'], dct['name'])

    def to_mongo_dict(self):
        return {'realm': self.realm, 'name': self.name, 'symbol': self.symbol, 'class': self.__class__.__name__}


class DealedTrans:
    """
    Property class is not easy, so complicated to make a best practice
    """

    def __str__(self):
        return '<{} {} {} {} {} {}>'.format(self.entrust_ref_key[:4] if self.entrust_ref_key else 'None', self.contract,
                                            self.bs, self.dealed_amount, self.dealed_price, self.dealed_time)

    @classmethod
    def from_dict(cls, dct):
        trans = cls()
        for key in cls.keys:
            if key in dct:
                setattr(trans, key, dct[key])
        if trans.account:
            trans.account = AccountApi.get_by_symbol(trans.account)
        if trans.contract:
            trans.contract = ContractApi.get_by_symbol(trans.contract)
        if trans.dealed_time:
            trans.dealed_time = dateutil.parser.parse(trans.dealed_time)
        return trans

    @staticmethod
    def from_ws_str_to_lst(message):
        rtn = []
        lst = json.loads(message)
        logging.debug(lst)
        for item in lst:
            con = ContractApi.get_by_symbol(item[0])
            tm = arrow.Arrow.fromtimestamp(item[1]).datetime
            dealed = DealedTrans(contract=con, dealed_time=tm, dealed_price=item[2], bs=item[3], dealed_amount=item[4])
            rtn.append(dealed)
        # logging.debug(rtn)
        return rtn

    @staticmethod
    def from_ws_str(message):
        item = json.loads(message)
        con = ContractApi.get_by_symbol(item[0])
        tm = arrow.Arrow.fromtimestamp(item[1]).datetime
        dealed = DealedTrans(contract=con, dealed_time=tm, dealed_price=item[2], bs=item[3], dealed_amount=item[4])
        logging.debug(dealed)
        return dealed

    """
    {
        "account" : "djw@huatai",
        "deal_no" : 2495, # used in broker systme, type string
        "entrust_no" : 3315, # connect to broker system, type string
        "deal_amount" : 500.0,
        "contract" : Contract
        "bs" : "b",
        "deal_time" : ISODate("2015-10-15T01:36:07Z"),
        "deal_price" : 0.922
        "entrust_ref_key": "oiO76234d..." # with length 40
    }
    """

    keys = ['account',
            'entrust_ref_key',
            'dealed_time',
            'dealed_price',
            'bs',
            'contract',
            'dealed_amount',
            'entrust_no',  # not required
            'dealed_no',  # not required
            ]

    def __init__(self, account=None, entrust_ref_key=None, dealed_time=None, dealed_price=None,
                 bs=None, contract=None, dealed_amount=None, entrust_no=None, dealed_no=None):
        self.account = account
        self.entrust_ref_key = entrust_ref_key
        self.dealed_time = dealed_time
        self.dealed_price = dealed_price
        self.bs = bs
        self.contract = contract
        self.dealed_amount = dealed_amount
        self.entrust_no = entrust_no
        self.dealed_no = dealed_no

    def human_str(self):
        return '{0.account} {0.bs} {0.dealed_price}'.format_map(self)

    def to_dict(self):
        body = {key: getattr(self, key) for key in self.keys}
        body['account'] = body['account'].symbol
        body['contract'] = body['contract'].symbol
        body['dealed_time'] = body['dealed_time'].isoformat()
        return body


class Order:
    """
    sample in the database
    {
      "_id" : ObjectId("561f1db1b8be1e372c2e12d0"),
      "accountid" : "djw@huatai",
      "entrust_price" : 0.922,
      "deal_amount" : 500.0,
      "deal_history" : [{
          "accountid" : "djw@huatai",
          "deal_no" : 2495,
          "entrust_no" : 3315,
          "deal_amount" : 500.0,
          "fund_code" : "159930",
          "bs" : "b",
          "deal_time" : ISODate("2015-10-15T01:36:07Z"),
          "deal_price" : 0.922
        }],
      "bs" : "b",
      "entrust_time" : ISODate("2015-10-15T01:36:07Z"),
      "entrust_status" : "已成",
      "date" : "2015-10-15",
      "avg_deal_price" : 0.922,
      "entrust_no" : 3315,
      "entrust_amount" : 500.0,
      "fund_code" : "159930"
      "option" : {'market' : true, ...}
    }

    """

    BUY = 'b'
    SELL = 's'

    def __init__(self, contract, entrust_price, bs, entrust_amount, account=None, entrust_time=None, ref_key="",
                 algo="", comment="", status="", entrust_no="", last_update=None,
                 version=0, last_dealed_amount=0, tags=None, options=None, commission=0):
        # account + entrust_time + entrust_no is unique
        # if entrust_time can be get from server, then use server one, else use local time
        # ref_key is using for callback, so ref_key is random string with length=32,
        # it can be sort by entrust_time, so order of ref_key is useless
        # ref_key is unique globally, accross machine, client, account, server
        assert bs == self.BUY or bs == self.SELL
        self.bs = bs
        self.entrust_price = entrust_price
        self.entrust_amount = entrust_amount
        self.contract = contract
        self.account = account
        self.entrust_no = entrust_no
        # self.average_deal_price = 0
        # self.deal_amount = 0
        if entrust_time:
            self.entrust_time = entrust_time
        else:
            self.entrust_time = arrow.now().datetime
        if last_update:
            self.last_update = last_update
        else:
            self.last_update = self.entrust_time
        self.ref_key = ref_key
        self.dealed_trans = []
        """:type: list[DealedTrans]"""
        self.algo = algo
        self.comment = comment
        self.status = status
        # version will increase 1 once the order status changed
        self.version = version
        # last change means the different deal amount compare with the last status of order
        self.last_dealed_amount = last_dealed_amount
        self.commission = commission
        self.tags = tags if tags else {}
        self.options = options if options else {}

    def inc_version(self):
        self.version += 1

    # @property
    # def avg_deal_price(self):
    #     warnings.warn('Use avg_dealed_price instead', DeprecationWarning, 2)
    #     logging.warning(util.get_caller())
    #     logging.warning('avg_deal_price deprecated')
    #     return self.avg_dealed_price

    @property
    def avg_dealed_price(self):
        if not self.dealed_amount:
            return 0
        q = sum(x.dealed_amount * x.dealed_price for x in self.dealed_trans)
        return q / self.dealed_amount

    # @property
    # def deal_amount(self):
    #     warnings.warn('Use dealed_amount instead', DeprecationWarning, 2)
    #     logging.warning(util.get_caller())
    #     logging.warning('deal amount deprecated')
    #     return sum(x.dealed_amount for x in self.dealed_trans)

    @property
    def dealed_amount(self):
        return sum(x.dealed_amount for x in self.dealed_trans)

    def to_dict(self):
        """
        okay, let's be more strict, this must be json compatible, which means datetime must be convert to isoformat
        :return:
        """
        t = {'bs': self.bs,
             'entrust_time': self.entrust_time.isoformat(),
             'entrust_no': self.entrust_no,
             'entrust_amount': self.entrust_amount,
             'entrust_price': self.entrust_price,
             'contract': self.contract,
             'account': self.account,
             'last_update': self.last_update.isoformat(),
             'dealed_trans': [x.to_dict() for x in self.dealed_trans],
             'ref_key': self.ref_key,
             'status': self.status,
             'version': self.version,
             'dealed_amount': self.dealed_amount,
             'avg_dealed_price': self.avg_dealed_price,
             'last_dealed_amount': self.last_dealed_amount,
             'tags': self.tags,
             'options': self.options,
             'commission': self.commission}
        return t

    @staticmethod
    def from_dict(dct) -> 'Order':
        acc = dct['account']
        o = Order(contract=dct['contract'],
                  entrust_price=dct['entrust_price'],
                  bs=dct['bs'],
                  entrust_amount=dct['entrust_amount'],
                  entrust_time=dateutil.parser.parse(dct['entrust_time']),
                  entrust_no=dct.get('entrust_no', ''),
                  account=acc,
                  last_update=dateutil.parser.parse(dct['last_update']),
                  ref_key=dct['ref_key'],
                  status=dct['status'],
                  version=dct['version'],
                  last_dealed_amount=dct['last_dealed_amount'],
                  commission=dct.get('commission', 0),
                  tags=dct.get('tags', {}),
                  options=dct.get('options', {}))
        for item in dct['dealed_trans']:
            o.dealed_trans.append(DealedTrans.from_dict(item))
        return o

    # entrust_time = datetime.fromtimestamp(js['Created'] / 1000, tz=util.gmtp8)

    # def add_deal_history(self, dealed_price, dealed_amount, dealed_time):
    #     logging.warning(util.get_caller())
    #     logging.warning('add deal history deprecated')
    #     self.dealed_trans.append(DealedTrans(account=self.account,
    #                                          entrust_ref_key=self.ref_key,
    #                                          contract=self.contract,
    #                                          bs=self.bs,
    #                                          dealed_time=dealed_time,
    #                                          dealed_amount=dealed_amount,
    #                                          dealed_price=dealed_price))

    def add_dealed_history(self, dealed_price, dealed_amount, dealed_time):
        self.dealed_trans.append(DealedTrans(account=self.account,
                                             entrust_ref_key=self.ref_key,
                                             contract=self.contract,
                                             bs=self.bs,
                                             dealed_time=dealed_time,
                                             dealed_amount=dealed_amount,
                                             dealed_price=dealed_price))

    def add_dealed_trans(self, dealed_price, dealed_amount, dealed_time):
        logging.debug('add dealed trans {} {} {}'.format(dealed_price, dealed_amount, dealed_time))
        self.dealed_trans.append(DealedTrans(account=self.account,
                                             entrust_ref_key=self.ref_key,
                                             contract=self.contract,
                                             bs=self.bs,
                                             dealed_time=dealed_time,
                                             dealed_amount=dealed_amount,
                                             dealed_price=dealed_price))

    # def set_deal_amount(self, new_deal_amount, new_avg_price=None):
    #     logging.warning(util.get_caller())
    #     logging.warning('set deal amount deprecated')
    #     return self.set_dealed_amount(new_deal_amount, new_avg_price)

    def set_dealed_amount(self, new_dealed_amount, new_avg_price=None):
        """
        will set last_dealed_amount
        :param new_dealed_amount:
        :param new_avg_price:
        :return:
        """
        logging.debug('set dealed amount {} {}'.format(new_dealed_amount, new_avg_price))
        diff_amount = new_dealed_amount - self.dealed_amount
        self.last_dealed_amount = diff_amount
        if diff_amount == 0:
            return
        if new_avg_price is None:
            self.add_dealed_history(self.entrust_price, diff_amount, util.gmtp8now())
        else:
            diff = new_avg_price * new_dealed_amount - self.avg_dealed_price * self.dealed_amount
            self.add_dealed_history(diff / diff_amount, diff_amount, util.gmtp8now())

    def __str__(self):
        if self.entrust_time:
            lst = (self.ref_key[:4], self.entrust_time.strftime('%H:%M:%S'), self.contract.symbol,
                   self.avg_dealed_price, self.entrust_price, self.bs, self.dealed_amount, self.entrust_amount,
                   self.status)
            return '<{} {} {} {}/{} {} {}/{} {}>'.format(*lst)
        else:
            return '(%s, %s,%s,%s,%s,%s)' % (
                self.ref_key, self.contract.symbol, self.entrust_price, self.bs, '---', self.entrust_amount)

    def __repr__(self):
        return str(self)

    ERROR_ORDER = 'error_order'

    WAITTING = 'waitting'  # received from strategy
    PENDING = 'pending'  # already send to broker, and received status update from broker, waitting for deal
    PART_DEAL_PENDING = 'part_deal_pending'
    WITHDRAWING = 'withdrawing'  # withdraw request send, wait for action
    PART_DEAL_WITHDRAWING = 'part_deal_withdrawing'  # similar with above, but when withdraw send, some already dealed

    DEALED = 'dealed'
    WITHDRAWED = 'withdrawed'  # STOP status
    PART_DEAL_WITHDRAWED = 'part_deal_withdrawed'  # STOP status

    ENDING_STATUSES = [ERROR_ORDER, DEALED, WITHDRAWED, PART_DEAL_WITHDRAWED]

    ALL_STATUSES = [WAITTING, PENDING, PART_DEAL_PENDING, WITHDRAWING, PART_DEAL_WITHDRAWING,
                    ERROR_ORDER, DEALED, WITHDRAWED, PART_DEAL_WITHDRAWED]


class OrderPool:
    def __init__(self, account):
        self.account = account
        self.pool = {}  # type: Dict[str, Order]
        self.map_e2r = {}

    def fetch(self, ref_key, create=False) -> Order:
        if not create:
            if ref_key not in self.pool:
                logging.warning('ref_key {} not in pool'.format(ref_key))
                raise Exception('ref_key {} not in pool'.format(ref_key))
        if ref_key not in self.pool:
            self.pool[ref_key] = Order(contract=None, entrust_price=0, bs='b', entrust_amount=0, account=self.account,
                                       ref_key=ref_key)
        return self.pool[ref_key]

    def to_df(self):
        return pd.DataFrame([v.to_dict() for k, v in self.pool.items()]).sort_values(by='entrust_time')

    def map_entrust_no_with_ref_key(self, order):
        logging.debug('mapping {} with {}'.format(order.ref_key, order.entrust_no))
        self.map_e2r[order.entrust_no] = order.ref_key

    def remove_order(self, o: Order):
        if o.entrust_no in self.map_e2r:
            del self.map_e2r[o.entrust_no]
        if o.ref_key in self.pool:
            del self.pool[o.ref_key]


class PositionList(list):
    def __init__(self):
        super().__init__()

    def __getitem__(self, item):
        if isinstance(item, int):
            return super().__getitem__(item)
        else:
            for x in self:
                if x.contract == item:
                    return x


class SmartOrder:
    CHASE = 'chase'  # deprecated
    LIMIT = 'limit'  # deprecated
    MARKETHARD = 'market_hard'  # depreacated

    LIMIT_PLUS = 'limit_plus'
    LIMIT_MINUS = 'limit_minus'
    MIDDLE = 'middle'
    LAST = 'last'
    MARKET = 'market'
    MARKET_HARD = 'market_hard'

    STATS = 'stats'  # pick strategy based on statistics
    RANDOM = 'random'  # pick strategy randomly (uniformly)
    ALL = [LIMIT_PLUS, MIDDLE, LAST, MARKET, MARKET_HARD, LIMIT_MINUS]

    @staticmethod
    def get_by_symbol(symbol):
        simple = re.sub(r'[^A-Za-z_]', '', symbol).upper()
        return getattr(SmartOrder, simple)


class TimeRange:
    ASHARE = ['ashare', '0930-1130', '1300-1500']


class Ticker(Model):
    def __init__(self, tm, price, volume=0, bids=None, asks=None, contract=None,
                 source=None,
                 exchange_time=None,
                 amount=None,
                 **kwargs):
        """
        :param datetime tm: time
        :param price:
        :param volume: 上一个tick到这一个tick之间的成交量
                       成交量 单位会比较奇怪 如果是现货的话 比如 btc.usd 单位就是btc
                       期货的话 单位各式各样 bitmex的单位是1美元 okex的单位是100美元(btc) 或者10美元(ltc)
        :param amount: 成交额 单位一定是rmb
        :param source: where the tick come from xueqiu/sina/exchange
        :param bids: [{'price': ..., 'volume': ...}, ...]
        :param asks: [{'price': ..., 'volume': ...}, ...]
        :return:
        """
        # internally use python3's datetime
        if isinstance(tm, arrow.Arrow):
            tm = tm.datetime
        assert tm.tzinfo
        self.contract = contract
        self.source = source
        self.tm = tm
        self.price = price
        self.volume = volume
        self.amount = amount
        self.bids = []
        self.asks = []
        self.exchange_time = exchange_time
        if bids:
            self.bids = sorted(bids, key=lambda x: -x['price'])
        if asks:
            self.asks = sorted(asks, key=lambda x: x['price'])
        for item in self.bids:
            assert 'price' in item and 'volume' in item and len(item) == 2
        for item in self.asks:
            assert 'price' in item and 'volume' in item and len(item) == 2
            # self.asks = asks

    # last as an candidate of last
    @property
    def last(self):
        return self.price

    @last.setter
    def last(self, value):
        self.price = value

    @property
    def time(self):
        return self.tm

    @time.setter
    def time(self, value):
        self.tm = value

    @property
    def bid1(self):
        if self.bids:
            return self.bids[0]['price']
        return None

    @property
    def ask1(self):
        if self.asks:
            return self.asks[0]['price']
        return None

    @property
    def weighted_middle(self):
        a = self.bids[0]['price'] * self.asks[0]['volume']
        b = self.asks[0]['price'] * self.bids[0]['volume']
        return (a + b) / (self.asks[0]['volume'] + self.bids[0]['volume'])

    def get_interest_side(self, bs):
        if bs == 's':
            return self.bids
        if bs == 'b':
            return self.asks

    def __str__(self):
        return '<{} {}.{:03d} {}/{} {} {}>'.format(self.contract,
                                                   self.time.strftime('%H:%M:%S'),
                                                   self.time.microsecond // 1000,
                                                   self.bid1,
                                                   self.ask1,
                                                   self.last,
                                                   self.volume)

    @staticmethod
    def init_with_dict(dct):
        return Ticker(dct['tm'], dct['price'], dct['volume'], dct['bids'], dct['asks'])

    def to_dict(self):
        dct = {'tm': self.tm.isoformat(), 'price': self.price, 'volume': self.volume, 'asks': self.asks,
               'bids': self.bids}
        if self.exchange_time:
            dct['exchange_time'] = self.exchange_time.isoformat()
        if self.contract:
            dct['symbol'] = self.contract.symbol
        return dct

    @staticmethod
    def from_dct(dct):
        con = ContractApi.get_by_symbol(dct['symbol'])
        return Ticker(tm=dateutil.parser.parse(dct['tm']), price=dct['price'], bids=dct['bids'], asks=dct['asks'],
                      contract=con, volume=dct['volume'])

    def to_mongo_dict(self):
        dct = {'tm': self.tm, 'price': self.price, 'volume': self.volume, 'asks': self.asks, 'bids': self.bids}
        if self.contract:
            dct['contract'] = self.contract.symbol
        return dct

    def to_short_list(self):
        b = ','.join(['{},{}'.format(x['price'], x['volume']) for x in self.bids])
        a = ','.join(['{},{}'.format(x['price'], x['volume']) for x in self.asks])
        lst = [self.contract.symbol, self.tm.timestamp(), self.price, self.volume, b, a]
        return lst

    @staticmethod
    def from_short_list(lst):
        if isinstance(lst[0], str):
            # convert string to contract
            lst[0] = ContractApi.get_by_symbol(lst[0])
        bids, asks = lst[4], lst[5]
        bids = [{'price': float(p), 'volume': float(v)} for p, v in zip(bids.split(',')[::2], bids.split(',')[1::2])]
        asks = [{'price': float(p), 'volume': float(v)} for p, v in zip(asks.split(',')[::2], asks.split(',')[1::2])]

        tm = arrow.Arrow.fromtimestamp(lst[1]).datetime
        return Ticker(contract=lst[0], tm=tm, price=lst[2], volume=lst[3], bids=bids, asks=asks)

    def to_ws_str(self):
        lst = self.to_short_list()
        return json.dumps(lst)

    def to_dict_v2(self):
        dct = {'time': self.tm.isoformat(), 'last': self.last, 'volume': self.volume, 'asks': self.asks,
               'bids': self.bids}
        if self.contract:
            dct['contract'] = self.contract.symbol
        if self.source:
            dct['source'] = self.source
        if self.exchange_time:
            dct['exchange_time'] = self.exchange_time.isoformat()
        if self.amount is not None:
            dct['amount'] = self.amount
        return dct

    @classmethod
    def from_dict_v2(cls, dict_or_str):
        if isinstance(dict_or_str, str):
            return cls.from_dict_v2(json.loads(dict_or_str))
        d = dict_or_str
        t = Ticker(tm=arrow.get(d['time']),
                   contract=ContractApi.get_by_symbol(d['contract']),
                   volume=d['volume'],
                   asks=d['asks'],
                   bids=d['bids'],
                   price=d['last'],
                   source=d.get('source', None),
                   )
        return t

    def bs1(self, bs):
        if bs == 'b':
            return self.bid1
        else:
            return self.ask1

    @classmethod
    def from_ws_str(cls, message):
        return cls.from_short_list(json.loads(message))


class Zhubi:
    def __init__(self, contract, price, bs, amount, time=None, source=None):
        self.contract = contract
        self.price = price
        self.bs = bs
        self.amount = amount
        self.time = time or arrow.now().datetime
        self.source = source

    def to_dict_v2(self):
        dct = {'time': self.time.isoformat(), 'price': self.price, 'bs': self.bs, 'amount': self.amount,
               'contract': self.contract.symbol}
        if self.source:
            dct['source'] = self.source
        return dct

    def __str__(self):
        return '({contract} {price} {bs} {amount} {time})'.format(**self.__dict__)


class TickerWithNetValue(Ticker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'netvalue' in kwargs:
            self.netvalue = kwargs['netvalue']
        else:
            self.netvalue = 0

    @property
    def detail_str(self):
        s = '%s %s %s ' % (self.price, self.netvalue, self.tm) + '\n'
        s += ' '.join('(%s,%s)' % (x['price'], x['volume']) for x in self.bids) + '\n'
        s += ' '.join('(%s,%s)' % (x['price'], x['volume']) for x in self.asks)
        return s

    def to_dict(self):
        dct = super().to_dict()
        dct['netvalue'] = self.netvalue
        return dct


def unixtimestamp(tm):
    import time
    return str(int(time.mktime(tm.timetuple())))


class Candle:
    def __init__(self, tm, array, contract, duration='1day'):
        self.tm = tm
        self.o = float(array[0])
        self.h = float(array[1])
        self.l = float(array[2])
        self.c = float(array[3])
        if len(array) == 5:
            self.v = float(array[4])
        else:
            self.v = 0
        self.ohlc = array
        self.contract = contract
        self.duration = duration

    def to_dict(self):
        return {'o': self.o, 'h': self.h, 'l': self.h, 'c': self.c, 'contract': self.contract,
                'duration': self.duration, 'tm': self.tm}

    def __str__(self):
        return str(self.tm) + ' (%.2f %.2f %.2f %.2f %.2f)' % (self.o, self.h, self.l, self.c, self.v)

    def __repr__(self):
        return str(self)


class InvalidtimeError(Exception):
    pass


# noinspection PyPep8Naming
class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class Currency:
    base = {'cny': 1, 'usd': 6.6, 'hkd': 0.83, 'jpy': 0.059, 'krw': 0.0058}

    # noinspection PyPep8Naming
    @classproperty
    def USDCNY(self):
        return self.convert('usd', 'cny')

    # noinspection PyPep8Naming
    @classproperty
    def HKDCNY(self):
        return self.convert('hkd', 'cny')

    # noinspection PyPep8Naming
    @classproperty
    def JPYCNY(self):
        return self.convert('jpy', 'cny')

    # noinspection PyPep8Naming
    @classproperty
    def KRWCNY(self):
        return self.convert('krw', 'cny')

    @classmethod
    def convert(cls, a, b):
        """
        convert(usd, cny) ---> 6.8

        :param a:
        :param b:
        :return:
        """
        return cls.base[a] / cls.base[b]


class Contract:
    @classmethod
    def convert(cls, con: 'Contract'):
        return cls(con.exchange, con.name, con.min_change, con.alias, con.category, con.first_day, con.last_day,
                   con.exec_price, con.currency)

    def __init__(self, exchange: 'Exchange', name: str, min_change=0.001, alias="", category='STOCK', first_day=None,
                 last_day=None, exec_price=None, currency=None, uid=None, **kwargs):
        assert isinstance(exchange, Exchange)
        assert isinstance(min_change, float) or isinstance(min_change, int)
        self.name = name
        self.exchange = exchange
        self.category = category
        # self.data = []
        # """:type: list[Ticker]"""
        # self.ohlc = defaultdict(list)
        # self.symbol = symbol
        self.min_change = min_change
        self.alias = alias
        self.exec_price = exec_price
        self.first_day = first_day  # the listing date of the contract
        self.last_day = last_day  # the last date that this contract could be executed
        self.currency = currency
        self.uid = uid  # the id use in postgres, for postgres use only

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def symbol(self):
        return self.name + ':' + self.exchange.symbol

    @property
    def short_symbol(self):
        suffix = self.exchange.symbol
        if suffix == 'exchange.cn.sse':
            suffix = 'sh'
        elif suffix == 'exchange.cn.sze':
            suffix = 'sz'
        else:
            suffix = suffix.replace('exchange.xtc', 'xtc')
            suffix = suffix.replace('exchange.cn', '')
        return self.name + ':' + suffix

    # @property
    # def symbol(self):
    #     return self.symbol

    def __str__(self):
        if self.exchange.realm == 'xtc':
            return '<Con:{}:{}>'.format(self.name, self.exchange.name)
        else:
            return '<Con:{}>'.format(self.name)

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.symbol)


class BondContract(Contract):
    pass


class ApiClient:
    sess = requests.session()

    retries = 4

    def __init__(self, host='http://localhost/'):
        self.host = host
        self.timeout = 5

    def get(self, endpoint, params=None):
        from . import util
        res = util.http_try(self.sess.get, url=self.host + endpoint, params=params, timeout=self.timeout)
        return res

    def post(self, endpoint, data=None):
        """
        it can only post json data, all my would be better follow json rule?
        :param endpoint:
        :param data:
        :return:
        """
        res = self.sess.post(url=self.host + endpoint, json=data, timeout=self.timeout)
        try:
            return res.json()
        except:
            logging.warning('get failed endpoint: {} params: {} res: {}'.format(self.host + endpoint, data, res))
            raise

    def put(self, endpoint, uid, data=None):
        """
        it can only post json data, all my would be better follow json rule?
        :param endpoint:
        :param uid:
        :param data:
        :return:
        """
        uid = str(uid)
        res = self.sess.put(url=self.host + endpoint + '/' + uid, json=data, timeout=self.timeout)
        try:
            return res.json()
        except:
            logging.warning(
                'put failed endpoint: {} params: {} res: {}'.format(self.host + endpoint + '/' + uid, data, res))
            raise

    def delete(self, endpoint, params=None):
        res = self.sess.delete(self.host + endpoint, params=params, timeout=self.timeout)
        try:
            return res.json()
        except:
            logging.warning('get failed endpoint: {} params: {} res: {}'.format(self.host + endpoint, params, res))
            raise


client = ApiClient()


class EndPoint:
    CONTRACTCOLLECTIONS = 'contract-collections'
    ETFDETAILS = 'etf-detail'
    EXCHANGES = 'exchanges'
    ACCOUNTS = 'accounts'
    ACCOUNTCONTAINERS = 'account-containers'
    CONTRACTS = 'contracts'
    DEALEDTRANS = 'dealed-trans'


class Format:
    JSON = 'JSON'
    DATAFRAME = 'DATAFRAME'


class TickerApi:
    @staticmethod
    def get_last(contract):
        from .quote import redis_client
        # t = client.get('tickers/{}/last'.format(contract.symbol))
        if isinstance(contract, Contract):
            t = redis_client.get('tick.v2:' + contract.symbol)
        else:
            t = redis_client.get('tick.v2:' + contract)
        # from . import Ticker
        return Ticker.from_dict_v2(t.decode('utf8'))

    @staticmethod
    async def get_last_async(contract):
        from . import util
        conn = await util.get_async_redis_conn()
        if isinstance(contract, Contract):
            contract = contract.symbol
        t = await conn.get('tick.v2:' + contract)
        # print(t)
        if t is None:
            raise ValueError(f'{contract} not exist')
        try:
            return Ticker.from_dict_v2(t)
        except:
            logging.exception('failed')
            raise ValueError(f'{contract} not exist')
