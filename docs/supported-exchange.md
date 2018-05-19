# 交易所

## 支持的交易所

|交易所|交易类型|交易所 Symbol|详细说明|国家|
|------|-------|------------------------|:---:|:------------:|
|[币安 Binance](https://www.binance.com)|币币交易|biannce|[币安 Binance](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#币安-binance)|日本|
|[Bitfinex](https://www.bitfinex.com)|币币交易|bitfinex|[Bitfinex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bitfinex)|英属维尔京群岛|
|[Bitfinex](https://www.bitfinex.com)|杠杆交易|bitfinex|[Bitfinex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bitfinex)|英属维尔京群岛|
|[Bitflyer](https://bitflyer.jp)|现货交易|bitflyer|[Bitflyer](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bitflyer)|日本|
|[Bitflyer](https://bitflyer.jp)|合约交易|bitflyex|[Bitflyer](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bitflyer)|日本|
|[Bithumb](https://www.bithumb.com)|现货交易|bithumb|[Bithumb](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bithumb)|韩国|
|[Bitmex](https://www.bitmex.com)|合约交易|bitmex|[Bitmex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bitmex)|塞舌尔|
|[Bittrex](https://bittrex.com)|币币交易|bittrex|[Bittrex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#bittrex)|美国|
|[Gate](https://gate.io)|币币交易|gate|[Gate](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#gate)|中国|
|[火币 Huobi](https://www.huobi.pro)|币币交易|huobip|[火币 Huobi](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#火币-huobi)|中国|
|[火币 Huobi](https://www.huobi.pro)|杠杆交易|huobim|[火币 Huobi](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#火币-huobi)|中国|
|[火币 Hadax](https://www.hadax.com)|币币交易|hadax|[火币 Huobi](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#火币-huobi)|新加坡|
|[OKex](https://www.okex.com)|币币交易|okex|[OKex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#okex)|中国, 美国|
|[OKex](https://www.okex.com)|合约交易|okef|[OKex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#okex)|中国, 美国|
|[Poloniex](https://www.poloniex.com)|币币交易|poloniex|[Poloniex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#poloniex)|美国|
|[Poloniex](https://www.poloniex.com)|杠杆交易|||美国|
|[Quoinex](https://quoinex.com)|币币交易|quoinex|[Quoinex](https://github.com/qbtrade/onetoken/wiki/Exchange-Markets#quoinex)|日本|


## 期货交易所

目前支持2家期货交易所，okex的合约交易和bitmex的期货

- okex的期货合约有3种，当周、次周、当季，具体交易规则可以参考OKex[说明文档](https://support.okex.com/hc/zh-cn/articles/115001627231-什么是虚拟合约-如何交易-)
- bitmex期货合约[说明文档](https://www.bitmex.com/app/tradingOverview)



## 交易所之间的一些差别

需要注意的是每个交易所都有细微的差异，以下文档详细说明了各个交易所的差异。

### 币安 Binance

#### 行情
币安的orderbook 限制了只会每秒来一个, 但是逐笔数据是实时的, 所以如果想要判断最及时的行情 可以使用逐笔数据
#### 交易
交易所代码: binance
* 请求限制每个ip的weight
* 一般接口限制每个ip的weight累加不得超过**每分钟1200**
* 交易接口限制每个账号**每秒10单，每天限制100000单**
* 查询订单信息**无法获得average_dealt_price**
* 单个交易对支持最近**500条**历史成交记录
* 币安会对下单使用机器学习的限制 具体详见 [币安API交易规则说明](https://support.binance.com/hc/zh-cn/articles/115003235691-%E5%B8%81%E5%AE%89API%E4%BA%A4%E6%98%93%E8%A7%84%E5%88%99%E8%AF%B4%E6%98%8E)
### Bitfinex

交易所代码: bitfinex
* 背后的接口用的是bitfinex v2的websocket
* bitfinex 的 v1 rest接口 非常不稳定

### Bitflyer

交易所代码: bitflyer（现货）
 bitflex (期货）

### bithumb

交易所代码: bithumb

### Bitmex

交易所代码: bitmex
* 交易频繁/行情剧烈的时候 bitmex经常会system overload
* bitmex 普通时候 交易数秒才能返回 都是正常的 (不是网络因素 他们系统的因素)

### Bittrex

交易所代码: bittrex
* 查询订单信息**无法获得entrust_price**
* 限制最多同时**500个**未成交订单
* 限制每天最多下**200000单**

### Gate

交易所代码: gate
* 用contract查询订单信息仅支持以下**3种**状态：pending, part-deal-pending, active
* 撤单时向交易所发送无效的exchange_oid(比如已经撤掉的单子)也会返回撤单成功，不会返回错误。
* 单个交易对支持最近**1天**的成交记录
* 交易所下单之后 要过两三秒钟才能查询到撤单  (如果你使用一个HTTP Session的话 速度会快一点 估计他们服务器内部有一些奇怪的缓存)

### 火币 Huobi

交易所代码: huobip(币币交易), huobim(杠杆交易)
* 查询订单信息时如果不添加contract会返回所有交易对的订单
* 单个交易对支持最近**1天**的成交记录
* 限制每个交易接口**10秒最多100次**请求 按用户限制
* 火币现在没有提供websocket接口. 所有查询都是通过rest的

### HADAX

* 首先去 https://www.hadax.com/zh-cn/ 登录并且开通交易
* 填入和huobip同样的api key和api secret

### OKex

交易所代码: okex, okef
* 单个交易对支持最近**2天**的成交记录
* 不支持查询成交记录  (dealt-trans接口)
* okex的websocket **非常非常非常** 不稳定 所以所有的接口都是通过rest的
* okex **号称** 马上就会上v2的接口(就是他们网页版使用的接口) 但是已经跳票好几个月了

### Poloniex

* 用contract查询订单信息仅支持以下**3种**状态：pending, part-deal-pending, active
* 单个交易对支持最近**1天**的成交记录

### Quoinex

交易所代码: quoinex
* 由于交易所严格限制请求次数，OneToken会缓存账户信息和下单信息**5秒**。
* 单个交易对支持最近**1000条**的成交记录

