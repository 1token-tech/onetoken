
# 命名规则


| | 规则 | 示例 | 详细解释 |
|:---:|:---:|:---:|:---|
|account|{exchange}/{user_name} | okex/demo|
|contract|{exchange}/{base}.{quote}(.{delivery}) | okex/btc.usdt或okef/btc.usd.n | 普通币币交易和杠杆交易两个币种用点（.）分隔，用quote货币计价来买卖base货币。合约交易在两个币种之后还要添加交割[时间标识](#期货交易代码)。
|client_oid|任意非空字符串| abc |由用户指定或者由OneToken随机生成，用于追踪账户信息。
|exchange_oid|{contract}-{string}| okex/btc.usd-123或okef/btc.usd.n-123 |由交易所生成，用于追踪订单信息。
|exchange_tid|{contract}-{string}| quoinex/btc.jpy-12345|由交易所生成，用于追踪历史成交信息。

### 币币交易代码

币币交易代码由3部分组成，`{exchange}/{underlying}.{quote_currency}`
例如：
```
binance/btc.usdt 表示币安交易所的usdt计价的btc交易
okex/eth.btc  表示okex交易所btc计价的eth交易
```


### 期货交易代码

期货交易代码由4部分组成，`{exchange}/{underlying}.{quote_currency}.{delivery}`
例如：
```
okef/btc.usd.i 表示ok交易所BTC合约的指数
okef/btc.usd.t 表示ok交易所BTC当周合约
okef/btc.usd.n 表示ok交易所BTC次周合约
okef/btc.usd.q 表示ok交易所BTC当季合约

bitmex/eth.btc.2018-06-29  表示bitmex交易所2018年6月29日到期的eth.btc合约
bitmex/btc.usd.td          表示bitmex交易所btc.usd的掉期合约

```
需要注意的是，okef的合约是连续的，当周交割后次周自动变为当周，因此不同时刻当周、次周、当季合约对应的到期日不是固定的。