![](https://img.shields.io/badge/PYTHON-3.5%2B-green.svg)


Btp SDK
====
BTP is a application to fetch tick and play with orders. BTP is a friendly python wrapper for ws API and restful API which will be introduce [here](#direct-api),  users can use API di.rectly as they like

Users can:

1. Streaming contract tick(via Quote).
2. Place, amend, cancel orders(via Account).
3. parse tick data (into|from) various form(short list, mongo dict, ws dict etc.)

### Supported Exchanges

* bitmex
* okex
* bithumb
* huobi pro
* bitfinex
* bitflyer
* bitstar
* bittrex
* poloniex
* gate
* exx
* coinegg

Currently the support of other exchanges is still under development.


### Get Started

```bash
pip install btp
```
Then use btc with `import btp` in python script.

### Example

Try Quote and Account class, the code is in './example'

`$ cd /path-you-clone-this-repo-to/`

if you don't want to install this package, set the `PYTHONPATH`

`$ export PYTHONPATH=.`

To try Quote:

`$ python example/quote.py`

To try Account, prepare your api_key and api_secret, then:

`$ python example/account.py`

api_key and api_secret will be required in the console.


### Tick


`time, price, volume, bids, asks, contract, source, exchange_time, amount`

some property function:

`last, bid1, ask1, weighted_middle`

parse to or from other forms:



```python
init_with_dict(dct)
to_dict()
from_dct(dct)
to_mongo_dict()
to_short_list()
from_short_list()
from_dict()
to_ws_str()
```


### Quote

To subscribe contract tick.


   
* `async def subscribe_tick(self, contract, on_update=None)`
    
    `contract`: str, contract name. e.g. `ltc.btc:xtc.okex`
    
    `on_update`: func, callback function, accept both `async` and `non-async` function.
   
   to subscribe a tick stream of contract, on_update will be called once new tick reach.
   
* `async def get_last_tick(self, contract)`
    
    `contract`: str, contract name. e.g. `ltc.btc:xtc.okex`
    
    to get the last tick of specific contract.

### Account

To perform account actions.

* `def __init__(self, symbol: str, api_key, api_secret, loop=None, host=None)`
    
    `symbol`: str, symbol
    
    `api_key`: str, api_key
    
    `api_secret`: str, api_secret
    
    `loop`:
    
    `host`: default to `http://alihk-debug.qbtrade.org:3019/trade`
    
    initialize an account for specific symbol with api_key and api_secret

* `async def get_pending_list(self)`
    
    get the list of orders on pending status
    
* `async def cancel_use_client_oid(self, oid)`

    `oid`: str, client_oid
    
    cancel orders with `oid`
    
* `async def cancel_use_exchange_oid(self, oid)`    

    `oid`: str, exchange_oid
    
    cancel orders with `oid`
    
* `async def cancel_all(self)`
    
    cancel all orders
    
* `async def get_info(self, timeout=15)`
    
    get account info
    
    return (info, err)
    
* `def get_total_amount(self, pos_symbol)`

    `pos_symbol`: str, symbol
    
    return position of symbol if symbol in position else 0.0
    
* `async def place_and_cancel(self, con, price, bs, amount, sleep, options=None)`

    `con`: str, contract
    
    `price`: number, wanted price
    
    `bs`: str, `'b'` or `'s'`, 'b' for buy, 's' for sell
    
    `amount`: number, wanted amount
    
    `sleep`: int, seconds between place and cancel
    
    `options`:
    
    place a order and cancel it after `sleep` seconds
    
* `async def get_status(self)`

    get status
    
* `async def get_order_use_client_oid(self, client_oid)`
    `async def get_order_use_exchange_oid(self, exchange_oid)`
    
    get order with client_oid or exchange_oid
    
* `async def amend_order_use_client_oid(self, client_oid, price, amount)`    
    `async def amend_order_use_exchange_oid(self, exchange_oid, price, amount)`
    
    `client_oid`|`exchange_oid`: str, oid
    
    `price`: number, wanted price
    
    `amount`: number, wanted amount
    
    amend specific order with new price and amount
    
* `async def place_order(self, con, price, bs, amount, client_oid=None, tags=None, options=None)`
    
    `con`: str, contract
    
    `price`: number, wanted price
    
    `bs`: str, `'b'|'s'`, to buy or to sell
    
    `amount`: number, wanted amount
    
    `client_oid`: str(len == 32),  client_oid is used to locate orders which will be generated randomly if not provided
    
    `tags`: dict, tags
    
    `options`:  
    
    place order
    
    return (res, err)



Direct API
===

Websocket API
--
### General

Connect your websocket client to `ws://alihk-debug.qbtrade.org:3019/ws`

A basic command is sent in the following format:
```$xslt
{
    'uri': '<command>',
    'args': {'arg1':'value1', 'arg2':'value2', ...}
}
```
The following commands are available without authentication:
* `subscribe-single-tick-verbose` subscribe a real-time ticker info of a given contract 

### Subscribe
Subscribe ticker
```$xslt
//request
{
    'uri': 'subscribe-single-tick-verbose', 
    'args': {'contract': '<contract>'}
}
```

### Heartbeat
```     
//webSocket Client request
{
    'uri': 'ping'
}

//webSocket Server response
{
    'uri': 'pong'
} 
```

RESTful API
--

Restful host is `http://alihk-debug.qbtrade.org:3019`

Just watch [todo](wait to solve)
    
