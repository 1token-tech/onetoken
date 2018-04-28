Manual
===

## 使用

* 运行Account示例程序前需要准备好OneToken的api_key和api_secret

    * 用户请访问[OneToken官网](https://1token.trade/)，按照[新手指引](https://1token.trade/r/ot-guide/index)注册账号，获取api_key和api_secret


### Python

    * 用户可以在自己开发的Python程序中导入onetoken模块

        ```
        import onetoken as ot
        ```

    * 运行示例程序`quote.py`获取行情Tick:

        `$ python quote.py`

    * 运行:

        `$ python account.py`

        根据命令行提示输入api_key和api_secret。

        ### Example

        Try Quote and Account class, the code is in './example'
        ```
        git clone https://github.com/qbtrade/onetoken
        cd onetoken/example
        ```

        if you don't want to install this package, set the `PYTHONPATH`

        `$ export PYTHONPATH=.`

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

        ### Account

        To perform account actions.

        * `def __init__(self, symbol: str, api_key, api_secret, loop=None, host=None)`

            `symbol`: str, symbol

            `api_key`: str, 1token api_key, generated in 1token

            `api_secret`: str, 1token api_secret, generate in 1token

            `loop`:

            `host`: default to `https://1token.trade/api/v1/trade`

            initialize an account for specific symbol with api_key and api_secret

        * `async def get_pending_list(self)`

            get the list of orders on pending status

        * `async def cancel_use_client_oid(self, oid, *oids)`

            `oid`: str, client_oid

            cancel orders with `oid`. Support multi oids, use `account.cancel_use_client_oid(oid1, oid2, ...)`

        * `async def cancel_use_exchange_oid(self, oid, *oids)`    

            `oid`: str, exchange_oid

            cancel orders with `oid`. Support multi oids, use `account.cancel_use_exchange_oid(oid1, oid2, ...)`

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

        * `async def get_order_use_client_oid(self, oid, *oids)`
            `async def get_order_use_exchange_oid(self, oid, *oids)`

            get order with client_oid or exchange_oid, support multi oids

            eg. `account.get_order_use_exchange_oid(oid1, oid2, oid3)`

            always return a list of orders

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
