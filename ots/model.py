import json

import arrow
import dateutil
import dateutil.parser


class Tick:
    def __init__(self, time, price, volume=0, bids=None, asks=None, contract=None,
                 source=None,
                 exchange_time=None,
                 amount=None,
                 **kwargs):

        # internally use python3's datetime
        if isinstance(time, arrow.Arrow):
            time = time.datetime
        assert time.tzinfo
        self.contract = contract
        self.source = source
        self.time = time
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

    def __repr__(self):
        return str(self)

    @staticmethod
    def init_with_dict(dct):
        return Tick(dct['time'], dct['price'], dct['volume'], dct['bids'], dct['asks'])

    def to_dict(self):
        dct = {'time': self.time.isoformat(), 'price': self.price, 'volume': self.volume, 'asks': self.asks,
               'bids': self.bids}
        if self.exchange_time:
            dct['exchange_time'] = self.exchange_time.isoformat()
        if self.contract:
            dct['symbol'] = self.contract
        return dct

    # @staticmethod
    # def from_dct(dct):
    #     # con = ContractApi.get_by_symbol(dct['symbol'])
    #     con = dct['symbol']
    #     return Tick(time=dateutil.parser.parse(dct['time']), price=dct['price'], bids=dct['bids'], asks=dct['asks'],
    #                 contract=con, volume=dct['volume'])

    def to_mongo_dict(self):
        dct = {'time': self.time, 'price': self.price, 'volume': self.volume, 'asks': self.asks, 'bids': self.bids}
        if self.contract:
            dct['contract'] = self.contract
        return dct

    def to_short_list(self):
        b = ','.join(['{},{}'.format(x['price'], x['volume']) for x in self.bids])
        a = ','.join(['{},{}'.format(x['price'], x['volume']) for x in self.asks])
        lst = [self.contract, self.time.timestamp(), self.price, self.volume, b, a]
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

        time = arrow.Arrow.fromtimestamp(lst[1]).datetime
        return Tick(contract=lst[0], time=time, price=lst[2], volume=lst[3], bids=bids, asks=asks)

    def to_ws_str(self):
        lst = self.to_short_list()
        return json.dumps(lst)

    @classmethod
    def from_dict(cls, dict_or_str):
        if isinstance(dict_or_str, str):
            return cls.from_dict(json.loads(dict_or_str))
        d = dict_or_str
        t = Tick(time=arrow.get(d['time']),
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
