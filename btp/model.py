import json
import logging
from typing import Dict

import arrow
import dateutil
import dateutil.parser
import pandas as pd

from . import util


class Model:
    def serialize(self, protocol):
        return protocol.dumps(self)


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
        # if trans.account:
        #     trans.account = AccountApi.get_by_symbol(trans.account)
        # if trans.contract:
        #     trans.contract = ContractApi.get_by_symbol(trans.contract)
        if trans.dealed_time:
            trans.dealed_time = dateutil.parser.parse(trans.dealed_time)
        return trans

    @staticmethod
    def from_ws_str_to_lst(message):
        rtn = []
        lst = json.loads(message)
        logging.debug(lst)
        for item in lst:
            # con = ContractApi.get_by_symbol(item[0])
            con = item[0]
            tm = arrow.Arrow.fromtimestamp(item[1]).datetime
            dealed = DealedTrans(contract=con, dealed_time=tm, dealed_price=item[2], bs=item[3], dealed_amount=item[4])
            rtn.append(dealed)
        # logging.debug(rtn)
        return rtn

    @staticmethod
    def from_ws_str(message):
        item = json.loads(message)
        # con = ContractApi.get_by_symbol(item[0])
        con = item[0]
        tm = arrow.Arrow.fromtimestamp(item[1]).datetime
        dealed = DealedTrans(contract=con, dealed_time=tm, dealed_price=item[2], bs=item[3], dealed_amount=item[4])
        logging.debug(dealed)
        return dealed

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
        body['dealed_time'] = body['dealed_time'].isoformat()
        return body


class Order:
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
            lst = (self.ref_key[:4], self.entrust_time.strftime('%H:%M:%S'), self.contract,
                   self.avg_dealed_price, self.entrust_price, self.bs, self.dealed_amount, self.entrust_amount,
                   self.status)
            return '<{} {} {} {}/{} {} {}/{} {}>'.format(*lst)
        else:
            return '(%s, %s,%s,%s,%s,%s)' % (
                self.ref_key, self.contract, self.entrust_price, self.bs, '---', self.entrust_amount)

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


class Ticker(Model):
    def __init__(self, tm, price, volume=0, bids=None, asks=None, contract=None,
                 source=None,
                 exchange_time=None,
                 amount=None,
                 **kwargs):

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
            dct['symbol'] = self.contract
        return dct

    @staticmethod
    def from_dct(dct):
        # con = ContractApi.get_by_symbol(dct['symbol'])
        con = dct['symbol']
        return Ticker(tm=dateutil.parser.parse(dct['tm']), price=dct['price'], bids=dct['bids'], asks=dct['asks'],
                      contract=con, volume=dct['volume'])

    def to_mongo_dict(self):
        dct = {'tm': self.tm, 'price': self.price, 'volume': self.volume, 'asks': self.asks, 'bids': self.bids}
        if self.contract:
            dct['contract'] = self.contract
        return dct

    def to_short_list(self):
        b = ','.join(['{},{}'.format(x['price'], x['volume']) for x in self.bids])
        a = ','.join(['{},{}'.format(x['price'], x['volume']) for x in self.asks])
        lst = [self.contract, self.tm.timestamp(), self.price, self.volume, b, a]
        return lst

    @staticmethod
    def from_short_list(lst):
        if isinstance(lst[0], str):
            # convert string to contract
            # lst[0] = ContractApi.get_by_symbol(lst[0])
            lst[0] = lst[0]
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
            dct['contract'] = self.contract
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
                   # contract=ContractApi.get_by_symbol(d['contract']),
                   contract=d['contract'],
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
               'contract': self.contract}
        if self.source:
            dct['source'] = self.source
        return dct

    def __str__(self):
        return '({contract} {price} {bs} {amount} {time})'.format(**self.__dict__)
