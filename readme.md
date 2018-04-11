![](https://img.shields.io/badge/PYTHON-3.6%2B-green.svg)


OneToken SDK
====
OneToken is a application to fetch tick and play with orders. OTS is a friendly python wrapper for ws API and restful API which will be introduce [here](#direct-api),  users can use API directly as they like

功能：

1. 获取行情tick(通过Quote)
2. 下单、撤单(通过Account)

### 支持交易所
<table>
<thead>
<tr>
<th>交易所</th>
<th>交易种类</th>
<th>交易所代码</th>
<th>详细说明</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="https://www.binance.com/">Binance</a>(日本)</td>
<td>币币交易</td>
<td>binance</td>
<td></td>
</tr>
<tr>
<td><a href="https://www.bitfinex.com/">Bitfinex</a>(英属维尔京群岛)</td>
<td>币币交易</td>
<td>bitfinex</td>
<td></td>
</tr>
<tr>
<td rowspan="2"><a href="https://bitflyer.jp/">Bitflyer</a>(日本)</td>
<td>币币交易</td>
<td>bitflyer</td>
<td></td>
</tr>
<tr>
<td>合约交易</td>
<td>bitflyex</td>
<td></td>
</tr>
<tr>
<td><a href="https://www.bithumb.com/">Bithumb</a>(韩国)</td>
<td>币币交易</td>
<td>bithumb</td>
<td></td>
</tr>
<tr>
<td><a href="https://www.bitmex.com/">Bitmex</a>(塞舌尔)</td>
<td>币币交易</td>
<td>bitfinex</td>
<td></td>
</tr>
<tr>
<td><a href="https://bittrex.com/">Bittrex</a>(美国)</td>
<td>币币交易</td>
<td>bittrex</td>
<td></td>
</tr>
<tr>
<td rowspan="3"><a href="https://www.huobipro.com/">火币</a>(中国)</td>
<td>币币交易</td>
<td>huobip</td>
<td></td>
</tr>
<tr>
<td>杠杆交易</td>
<td>huobim</td>
<td></td>
</tr>
<tr>
<td>合约交易</td>
<td>hadax</td>
<td></td>
</tr>
<tr>
<td rowspan="2"><a href="https://www.okex.com/">OKEX</a>(中国、美国)</td>
<td>币币交易</td>
<td>okex</td>
<td></td>
</tr>
<tr>
<td>合约交易</td>
<td>okef</td>
<td></td>
</tr>
<tr>
<td><a href="https://www.huobipro.com/">Poloniex</a>(美国)</td>
<td>币币交易</td>
<td>poloniex</td>
<td></td>
</tr>
</tbody>
</table>

目前只支持以上交易所，其他交易所会陆续上线。


### 安装步骤

* Python
    
    * 系统需求：Python 3.6
    
    * 安装onetoken
    
        ```bash
        $ pip install onetoken -U
        ```
    

### 命名规则

| | 规则 | 示例 | 详细解释 |
|:---:|:---:|:---:|:---|
|account|{exchange}/{specific_id} | okex/demo1| <交易所>/<用户名>
|contract| {exchange}/{tpa}.{tpb} | okex/btc.usdt | <交易所>/<交易对>，用点（.）分隔两个币种
|client_oid|任意非空字符串 | okex/btc.usdt-xxx |用于追踪订单信息，{specific_id}由用户指定或者由OneToken随机生成
|exchange_oid|{exchange}/{tpa}.{tpb}-{specific_id} | okex/btc.usdt-xxx |用于追踪订单信息，{specific_id}由交易所生成 


### 使用

* 用户可以在自己开发的Python程序中导入onetoken模块

    ```
    import onetoken as ot
    ```

* 运行示例程序`quote.py`获取行情Tick:

    `$ python quote.py`

* 运行示例程序Account前需要准备好OneToken的api_key和api_secret

    * 用户可以访问[OneToken官网](https://1token.trade/)按照[新手指引](https://1token.trade/r/ot-guide/index)注册账号，获取api_key和api_secret
    
    * 运行:
    
        `$ python account.py`
    
        根据命令行提示输入api_key和api_secret。




### Account支持的操作

* `def __init__(self, symbol: str, api_key, api_secret, loop=None, host=None)` 

    用OneToken系统的api_key和api_secret初始化账户
    
    * 参数： 
        
        `symbol`: str，账户标识，格式为<交易所代码>/<用户名>，例如binance/xxx
    
        `api_key`: str, OneToken api_key
    
        `api_secret`: str, OneToken api_secret
    
        `loop`:
    
        `host`: 默认为[https://1token.trade/api/v1/trade](https://1token.trade/api/v1/trade)
    
    * 返回值：`Account`对象


* `async def get_info(self, timeout=15)`
    
    获取账户信息
    
    * 参数：
    
        `timeout`: int，超时，可选，默认15秒
        
    * 返回值：`(info, err)`
        
        `info`: dict
        
        ```$xslt
        {
            "balance": 589943.9724,                 # float, 现金 + 虚拟货币市值
            "cash": 6198.5392,                      # float, 现金（根据人民币汇率计算）
            "market_value: 583745.4332,             # float, 虚拟货币市值
            "market_value_detail: {
                eos: 583745.4332,
                usdt: 0
            },
            "position": [
                {
                    "contract": "eos.usdt",         # str, "<coin>.<base>" 
                    "market_value": 583745.4332,    # float, market value of the contract
                    "amount_coin": 20071.4762,      # float, total amount of coins
                    "available_coin": 18971.4762,   # float, available amount of coins
                    "frozen_coin": 1100.0,          # float, frozen amount of coins
                    "pl_coin": 0,                   # float, pl_coin = profit and lose (or interest) of coins 
                    "loan_coin": 0,                 # float, loan of coins
                    market_value_detail: {
                        "eos": 583745.4332,
                        "usdt": 0
                    },
                    "value_cny": 0,                 # float, CNY value of the contract (if available)
                    "type": "margin",               # str, position type 
                    "mv_coin": 583745.4332,         # float, market value of coins
                    "amount_base": 979.0929,        # float, total amount of the base currency  
                    "mv_base": 0,                   # float, market value of the base currency, 0 for USDT
                    "available_base": 7029.3753,    # float, amount of the available base currency
                    "frozen_base": 4511.19,         # float, frozen amount of the base currency
                    "pl_base": -73.4164,            # float, pl_base = profit and lose (or interest) of the base currency
                    "loan_base": -10448.056,        # float, loan of the base currency 
                    "value_cny_base": 6198.5392     # CNY value of the base currency (if available)
                },
                ...
            ]
        }
        ```
        
        `err`: `{"code":"...", "message":"..."}`


* `async def place_order(self, con, price, bs, amount, client_oid=None, tags=None, options=None)`
    
    下单交易
    
    * 参数：
    
        `con`: str, 合约标识，格式为<交易所代码>/<交易对>，例如binance/btc.usdt
        
        `price`: number, 单价
        
        `bs`: str， `"b"`对应买或`"s"`对应卖
        
        `amount`: number, 数量
        
        `client_oid`: str(len == 32), 可选，如果不输入系统会生成随机的`client_oid`
        
        `tags`: dict
        
        `options`:  
    
    * 返回值：`(res, err)`
    
        `res`: `{"exchange_oid":"xxx", "client_oid":"xxx"}`
        
        `err`: `{"code":"...", "message":"..."}`


* `async def place_and_cancel(self, con, price, bs, amount, sleep, options=None)`
    
    下单后撤单
    
    * 参数：
    
        `con`: str, 合约标识，格式为<交易所代码>/<交易对>，例如binance/btc.usdt
        
        `price`: number, 单价
        
        `bs`: str，`"b"`对应买或`"s"`对应卖
        
        `amount`: number, 数量
    
        `sleep`: int, 下单和撤单之间的时间间隔，单位：秒
        
        `options`:
    
    * 返回值：`(res, err)`
    
        `res`: `{"exchange_oid":"xxx", "client_oid":"xxx"}`
        
        `err`: `{"code":"...", "message":"..."}`


* `async def get_order_use_client_oid(self, client_oid)`    
    `async def get_order_use_exchange_oid(self, exchange_oid)`
    
    用`client_oid`或`exchange_oid`获取订单信息
    
    * 参数：
    
        `client_oid|exchange_oid`: str，支持由逗号（,）隔开的多个订单号，例如binance/btc.usdt-xxx1,binance/btc.usdt-xxx2
    
    * 返回值：`(order, err)`
    
        `order`: dict
        
        ```$xslt
        {
            "account": "binance/test_account",              # 账户名
            "average_dealt_price": 112.1,                   # 平均成交价
            "bs": "b",                                      # `"b"`对应买或`"s"`对应卖
            "client_oid": "binance/ltc.usdt-xxx123",        # 由用户给定或由OneToken系统生成的订单追踪ID
            "comment": "string",                            # 
            "commission": 0.0025,                           # 成交手续费
            "contract": "binance/ltc.usdt",                 # 合约标识
            "dealt_amount": 1,                              # 成交数量
            "entrust_amount": 10,                           # 委托数量
            "entrust_price": 113,                           # 委托价格
            "entrust_time": "2018-04-03T12:21:13+08:00",    # 成交价格
            "exchange_oid": "binance/ltc.usdt-xxx456",      # 由交易所生成的订单追踪ID
            "last_dealed_amount": 0.8,                      # 最近一次成交数量
            "last_update": "2018-04-03T12:22:56+08:00",     # 最近更新时间
            "options": {},                                  # 
            "status": "part-deal-pending",                  # 订单状态
            "tags": {}                                      # 
        }
        ```
        
        `err`: dict，如果查询部分订单成功，`err["code"]`值为`"partial-success"`，并且附带`"data"`字段，其中包含成功查询到的订单信息和错误的订单号
        
        ```$xslt
        {
            "code": "partial-success"
            "message": ""
            "data": {
                        "success": [{订单详细信息},...]
                        "error": [{"exchange_oid":"xxx", "client_oid":"xxx"},...]
                    }
        }
        ```


* `async def get_order_list(self, contract, state)`

    * 参数：
    
        `contract`: str, 合约标识，格式为<交易所代码>/<交易对>，例如binance/btc.usdt
        
        `state`: str， 订单状态，支持activating、end等11种订单状态，下图描述了每个订单的生命周期
        
        ![订单生命周期](https://raw.githubusercontent.com/qbtrade/onetoken/readme/doc/OTS_Order_Status.png)
    
    * 返回值：`(res, err)`
        
        `res`: list，列表包含多个dict对象，参考get_order_use_client_oid

        `err`: `{"code":"...", "message":"..."}`


* `async def cancel_order_use_client_oid(self, client_oid)`    
    `async def cancel_order_use_exchange_oid(self, exchange_oid)`   
    
    用`client_oid`或`exchange_oid`取消订单
    
    * 参数：
    
        `client_oid|exchange_oid`: str，格式为<交易所代码>/<交易对>-<字符串>，支持由逗号（,）隔开的多个订单号，例如binance/btc.usdt-xxx1,binance/btc.usdt-xxx2
    
    * 返回值：`(res, err)`
    
        `res`: `{"exchange_oid":"xxx", "client_oid":"xxx"}`

        `err`: dict，如果取消部分订单成功，`err["code"]`值为`"partial-success"`，并且附带`"data"`字段，其中包含成功取消和错误的订单号
        
        ```$xslt
        {
            "code": "partial-success"
            "message": ""
            "data": {
                        "success": [{"exchange_oid":"xxx", "client_oid":"xxx"},...]
                        "error": [{"exchange_oid":"xxx", "client_oid":"xxx"},...]
                    }
        }
        ```
        

* `async def cancel_all(self)`
    
    取消所有未完全成交的订单
    
    * 参数：无
    
    * 返回值：`(res, err)`
    
        `res`: `{"status":"success"}`

        `err`: dict，如果取消部分订单成功，`err["code"]`值为`"partial-success"`，并且附带`"data"`字段，其中包含成功取消和错误的订单号
        
        ```$xslt
        {
            "code": "partial-success"
            "message": ""
            "data": {
                        "success": [{"exchange_oid":"xxx", "client_oid":"xxx"},...]
                        "error": [{"exchange_oid":"xxx", "client_oid":"xxx"},...]
                    }
        }
        ```


* `def get_total_amount(self, pos_symbol)`
    
    获取账户头寸

    * 参数：
    
        `pos_symbol`: str, symbol
    
    * 返回值：float, position of symbol if symbol in position else 0.0

    
* `async def get_status(self)`

    * 参数：无
    
    * 返回值：int，1到100之间
    

* `async def amend_order_use_client_oid(self, client_oid, price, amount)`    
    `async def amend_order_use_exchange_oid(self, exchange_oid, price, amount)`
    
    用`client_oid`或`exchange_oid`修改订单
    
    * 参数：
    
        `client_oid|exchange_oid`: str，格式为<交易所代码>/<交易对>-<字符串>
        
        `price`: number, 单价
        
        `amount`: number, 数量
    
    * 返回值：`(res, err)`
        
        `res`: 
        
        `err`: `{"code":"...", "message":"..."}`


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


Direct API
===

Websocket API
--
### General

Connect your websocket client to `wss://1token.trade/api/v1/quote/ws`

A basic command is sent in the following format:
```$xslt
{
    "uri": "<command>",
    "args": {"arg1":"value1", "arg2":"value2", ...}
}
```
The following commands are available without authentication:
* `subscribe-single-tick-verbose` subscribe a real-time ticker info of a given contract 

### Subscribe
Subscribe ticker
```$xslt
//request
{
    "uri": "subscribe-single-tick-verbose", 
    "args": {"contract": "<contract>"}
}
```

### Heartbeat
```     
//webSocket Client request
{
    "uri": "ping"
}

//webSocket Server response
{
    "uri": "pong"
} 
```

RESTful API
--

Restful host is `https://1token.trade/api/v1/trade`

API Explorer(https://1token.trade/r/swagger)




