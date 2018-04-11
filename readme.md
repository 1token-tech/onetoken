![](https://img.shields.io/badge/PYTHON-3.6%2B-green.svg)


OneToken SDK
====
OneToken is a application to fetch tick and play with orders. OTS is a friendly python wrapper for ws API and restful API which will be introduce [here](#direct-api),  users can use API directly as they like

功能：

1. 获取行情tick(通过Quote)
2. 下单、撤单(通过Account)

### 支持交易所
| 交易所                                 | 交易所代码        | 文档                                                                                         | 国家           |
|----------------------------------------|-------------------|:--------------------------------------------------------------------------------------------:|----------------|
|[币安](https://www.binance.com )        | binance           | [API](https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md) | 日本           |
|[Bitfinex](https://www.bitfinex.com)    | bitfinex          | [API](https://bitfinex.readme.io/v1/docs)                                                    | 英属维尔京群岛 |
|[Bitflyer](https://bitflyer.jp)         | bitflyer          | [API](https://bitflyer.jp/API)                                                               | 日本           |
|[Bitflyer合约交易](https://bitflyer.jp) | bitflyex          | [API](https://bitflyer.jp/API)                                                               | 日本           |
|[Bithumb](https://www.bithumb.com)      | bithumb           | [API](https://www.bithumb.com/u1/US127)                                                      | 韩国           |
|[Bitmex](https://www.bitmex.com)         | bitmex            | [API](https://www.bitmex.com/app/apiOverview)                                               | 塞舌尔         |
|[Bittrex](https://bittrex.com)           | bittrex           | [API](https://bittrex.com/Home/Api)                                                         | 美国           |
|[火币Pro](https://www.huobipro.com/)     | huobip            | [API](https://github.com/huobiapi/API_Docs/wiki/REST_api_reference)                         | 中国           |
|[火币杠杆交易](https://www.huobipro.com/)| huobim            | [API](https://github.com/huobiapi/API_Docs/wiki/REST_api_reference)                         | 中国           |
|[火币Hadax](https://www.hadax.com/)      | hadax            | [API](https://github.com/huobiapi/API_Docs/wiki/REST_api_reference)                          | 中国           |
|[Poloniex](https://poloniex.com/)       | poloniex          | [API](https://github.com/huobiapi/API_Docs/wiki/REST_api_reference)                          | 美国           |

目前只支持以上交易所，其他交易所会陆续上线。

### 系统需求
- python 3.6

### 开始使用
获取OneToken SDK
```
$ git clone https://github.com/qbtrade/onetoken
```
安装
```bash
$ pip install onetoken -U
```

如果不想安装，可以用以下代码设置`PYTHONPATH`环境变量
```
$ cd onetoken
$ export PYTHONPATH=$PYTHONPATH:.
```

然后在Python程序中导入onetoken模块
```
import onetoken as ot
```

### 示例

To try Quote:

`$ python quote.py`

To try Account, prepare your api_key and api_secret, then:

`$ python account.py`

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
to_short_list()
from_short_list()
from_dict()
to_ws_str()
```

### Contract

 `name, exchange, symbol, min_change, min_amount, unit_amount`
 - `min_change`: price precision, minimum change of entrust price
 - `min_amount`: minimum amount of an entrust
 - `unit_amount`: entrust amount precision, minimum change of entrust amount

To get supported contracts by exchange, use:

```$xslt
quote.get_contracts(exchange)
```

To get a certain contract, use:
```$xslt
quote.get_contract(symbol)
```
`symbol`: exchange/name, for example: `binance/btc.usdt`

### Quote

To subscribe contract tick.
   
* `async def subscribe_tick(self, contract, on_update=None)`
    
    `contract`: str, contract name. e.g. `ltc.btc:xtc.okex`
    
    `on_update`: func, callback function, accept both `async` and `non-async` function.
   
   to subscribe a tick stream of contract, on_update will be called once new tick reach.
   
* `async def get_last_tick(self, contract)`
    
    `contract`: str, contract name. e.g. `ltc.btc:xtc.okex`
    
    to get the last tick of specific contract.
                
### Account支持的操作

* `def __init__(self, symbol: str, api_key, api_secret, loop=None, host=None)`
    
    `symbol`: str，账户标识，格式为<交易所代码>/<用户名>，例如binance/xxx
    
    `api_key`: str, 1token api_key
    
    `api_secret`: str, 1token api_secret
    
    `loop`:
    
    `host`: 默认为[https://1token.trade/api/v1/trade](https://1token.trade/api/v1/trade)
    
    用OneToken分配的api_key和api_secret初始化账户

* `async def get_order_list(self, contract, state)`
    
    `contract`: str, 合约标识，格式为<交易所代码>/<交易对>，例如binance/btc.usdt
    `state`: str， 订单状态，支持activating、end等11种订单状态，下图描述了每个订单的生命周期
    |![gatecoin](https://github.com/qbtrade/onetoken/doc/OTS_Order_Status.png)
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
    
    info has the following format:
    
    ```$xslt
    {
        'balance': 589943.9724,  // float, cash + market value
        'cash': 6198.5392,  // float
        'market_value: 583745.4332,  // float, total market value
        'market_value_detail: {
            eos: 583745.4332,
            usdt: 0
        },
        'position': [
            {
                'contract': 'eos.usdt',  // str, '<coin>.<base>' 
                'market_value': 583745.4332,  // float, market value of the contract
                'amount_coin': 20071.4762,  //  float, total amount of coins
                'available_coin': 18971.4762, //  float, available amount of coins
                'frozen_coin': 1100.0,  // float, frozen amount of coins
                'pl_coin': 0,  // float, pl_coin = profit and lose (or interest) of coins 
                'loan_coin': 0,  // float, loan of coins
                market_value_detail: {
                    'eos': 583745.4332,
                    'usdt': 0
                },
                'value_cny': 0,  //  float, CNY value of the contract (if available)
                'type': 'margin',  // str, position type 
                'mv_coin': 583745.4332,  // float, market value of coins
                'amount_base': 979.0929,  //  float, total amount of the base currency  
                'mv_base': 0,  // float, market value of the base currency, 0 for USDT
                'available_base': 7029.3753,  // float, amount of the available base currency
                'frozen_base': 4511.19,  // float, frozen amount of the base currency
                'pl_base': -73.4164,  // float, pl_base = profit and lose (or interest) of the base currency
                'loan_base': -10448.056,  //  float, loan of the base currency 
                'value_cny_base': 6198.5392  // CNY value of the base currency (if available)
            },
            ...
        ]
    }
    ```
    
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

Connect your websocket client to `wss://1token.trade/api/v1/quote/ws`

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

Restful host is `https://1token.trade/api/v1/trade`

API Explorer(https://1token.trade/r/swagger)


命名规则
===
| | rule | example | explaination |
|:---:|:---:|:---:|:---|
|contract| {exchange}/{tpa}.{tpb} | okex/btc.usdt | tpa/tpb means "trading pair a/b"; use latter in the trading pair to buy and sell the former in exchange; the example means it uses usdt to sell and buy btc in okex
|account|{exchange}/{specific_id} | okex/demo1| putting the exchange in account makes it more readable and recognizable

