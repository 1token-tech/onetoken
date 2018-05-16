
# Official Documentation 1Token APIs and Streams.


## 手工交易者

## API 用户

### 基本信息

基本信息的api可以拿到所有的交易所列表

以及一个交易所的所有的支持交易对（contract）的列表

交易对的信息包括
* min_change 价格跳动的最小单位
* min_amount 下单的最小单位
* min_notional 下单的最小资产 （ price * amount )
* symbol 交易对的唯一标示  ${exchange}/${currency}.${underlying}

详细api请参考 [基本信息API](https://1token.trade/r/swagger?url=/r/swagger/basic.yml)


### 行情API

行情API支持websocket以及rest的方式去获取最新的行情信息

* [Rest API](https://1token.trade/r/swagger?url=/r/swagger/quote.yml)

* [Websocket API](./a/api-refer/ws-api.md)



### 交易API

[交易API](https://1token.trade/r/swagger?url=/r/swagger/trade.yml)

### 历史数据API

你可以通过API去下载所有的历史tick行情
