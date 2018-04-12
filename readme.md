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
<td><a href="https://www.binance.com/">Binance</a></td>
<td>币币交易</td>
<td>binance</td>
<td></td>
</tr>
<tr>
<td><a href="https://www.bitfinex.com/">Bitfinex</a></td>
<td>币币交易</td>
<td>bitfinex</td>
<td></td>
</tr>
<tr>
<td rowspan="2"><a href="https://bitflyer.jp/">Bitflyer</a></td>
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
<td><a href="https://www.bithumb.com/">Bithumb</a></td>
<td>币币交易</td>
<td>bithumb</td>
<td></td>
</tr>
<tr>
<td><a href="https://www.bitmex.com/">Bitmex</a></td>
<td>币币交易</td>
<td>bitfinex</td>
<td></td>
</tr>
<tr>
<td><a href="https://bittrex.com/">Bittrex</a></td>
<td>币币交易</td>
<td>bittrex</td>
<td></td>
</tr>
<tr>
<td rowspan="3"><a href="https://www.huobipro.com/">火币</a></td>
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
<td rowspan="2"><a href="https://www.okex.com/">OKEX</a></td>
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
<td><a href="https://www.huobipro.com/">Poloniex</a></td>
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
|account|{exchange}/<user_name> | okex/demo|
|contract|{exchange}/{base}.{quote}(.{delivery}) | okex/btc.usdt或okef/btc.usd.n | 普通币币交易和杠杆交易两个币种用点（.）分隔，用quote货币计价来买卖base货币。合约交易在两个币种之后还要添加交割时间标识。
|client_oid|任意非空字符串| abc |由用户指定或者由OneToken随机生成，用于追踪订单信息。
|exchange_oid|{contract}-{string} | okex/btc.usd-123或okef/btc.usd.n-123 |由交易所生成，用于追踪订单信息。


### 使用

* 运行Account示例程序前需要准备好OneToken的api_key和api_secret

    * 用户请访问[OneToken官网](https://1token.trade/)，按照[新手指引](https://1token.trade/r/ot-guide/index)注册账号，获取api_key和api_secret
    
    
* Python

    * 用户可以在自己开发的Python程序中导入onetoken模块
    
        ```
        import onetoken as ot
        ```
    
    * 运行示例程序`quote.py`获取行情Tick:
    
        `$ python quote.py`
    
    * 运行:
    
        `$ python account.py`
    
        根据命令行提示输入api_key和api_secret。


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