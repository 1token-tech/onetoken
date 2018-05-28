# 交易所的详细介绍

需要注意的是每个交易所都有细微的差异，以下文档详细说明了各个交易所的差异。

## 币安 Binance

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
* websocket 
* cancel all 不需要contract参数
* order list:
    * open orders list 不需要contract参数
    * all orders 需要contract参数
* get_order: 不支持avg_dealt_price，值为None
* get_order_list: 不支持avg_dealt_price，值为None
    

## ZB

交易所代码: zb
* 不支持dealt-trans，交易所完全没有成交记录这个概念, 网页上可以查询到账单，但是API并不提供支持
* 杠杆交易尚未支持
* 没有原生trans接口
* get_trans_list: 在最近100单里找成交过的单子，转换成trans,拿不到exchange_tid
* get_order_list: 会多次发送多次请求到交易所然后返回所有active状态的orders，但是end状态最多只有100条


## Bitfinex

交易所代码: bitfinex
* 背后的接口用的是bitfinex v2的websocket
* bitfinex 的 v1 rest接口 非常不稳定
* order_list： 不需要contract参数
* cancel all：不需要contract参数

## Bitflyer

交易所代码: bitflyer（现货）
 bitflex (期货）
 OTSDealtTrans: 没有taker/maker

## bithumb

交易所代码: bithumb
* OTSDealtTrans：
    * 没有exchange_tid
    * 没有taker/maker


## Bitmex

交易所代码: bitmex
* 交易频繁/行情剧烈的时候 bitmex经常会system overload
* bitmex 普通时候 交易数秒才能返回 都是正常的 (不是网络因素 他们系统的因素)
* order list: 不需要contract参数
* cancel all: 不需要contract参数


## Bittrex

交易所代码: bittrex
* 查询订单信息**无法获得entrust_price**
* 限制最多同时**500个**未成交订单
* 限制每天最多下**200000单**
* 没有原生trans接口
* order list: 不需要contract参数
* cancel all: 不需要contract参数
* trans list: 不需要contract参数
* OTSDealtTrans:
    * 没有commission
    * 没有commission_currency
    * 没有exchange_oid
    * 没有dealt_time
    * 没有taker/maker
* get_order: 除了调用single call的get_order还要在open_orders里找


## Gate

交易所代码: gate
* 用contract查询订单信息仅支持以下**3种**状态：pending, part-deal-pending, active
* 撤单时向交易所发送无效的exchange_oid(比如已经撤掉的单子)也会返回撤单成功，不会返回错误。
* 单个交易对支持最近**1天**的成交记录
* 交易所下单之后 要过两三秒钟才能查询到撤单  (如果你使用一个HTTP Session的话 速度会快一点 估计他们服务器内部有一些奇怪的缓存)
* order list: 不需要contract参数，只支持pending list
* OTSDealtTrans:
    * 没有commission
    * 没有commission_currency
    * 没有taker/maker

## 火币 Huobi

交易所代码: huobip(币币交易), huobim(杠杆交易)
* 可以查询所有的挂单 但是这个方法在火币的document里面是不存在的（他们doc要求一定要传入contract） 所以查询所有挂单这个请求可能失效
* 查询订单信息时如果不添加contract会返回所有交易对的订单
* 单个交易对支持最近**1天**的成交记录
* 限制每个交易接口**10秒最多100次**请求 按用户限制
* 火币现在没有提供websocket接口. 所有查询都是通过rest的
* order list: 不需要contract参数，但官方文档不支持
* cancel all: 不需要contract参数
* get_order：除了调用single call的get_order还要在open_orders里找
* get_accounts: 获得account_id


## HADAX

交易所代码：hadax
* 首先去 https://www.hadax.com/zh-cn/ 登录并且开通交易
* 填入和huobip同样的api key和api secret
* api 的行为和huobi保持一致

## OKex

交易所代码: okex
* 单个交易对支持最近**2天**的成交记录
* 不支持查询成交记录  (dealt-trans接口)
* 不支持拿所有的挂单
* okex的websocket **非常非常非常** 不稳定 所以所有的接口都是通过rest的
* okex **号称** 马上就会上v2的接口(就是他们网页版使用的接口) 但是已经跳票好几个月了
* 没有原生trans接口
* OTSDealtTrans:
    * commission: 没有
    * commission_currency: 没有
    * exchange_tid: 没有
    * dealt_time: 没有
    * taker/maker: 没有
* get_order: 除了调用single call的get_order还要在open_orders里找,拿不到手续费
* get_order_list: 拿不到手续费


## OKef

交易所代码: okef
* 现阶段只支持 全仓 20倍杠杆 如果不是全仓20倍杠杆，需要手动去账户上平仓，然后改成全仓20倍杠杆
* api 不支持开仓和平仓的选择 每次下单前会检查是否有足够仓位可以平仓 如果有的话 会尝试平仓，如果仓位不够平仓 则会主动开仓
  * 例子 如果现在持有2张多头 请求 sell 1张 则会去平掉这一张
  * 例子 如果现在持有2张多头 请求 sell 3张 则会开出3张空单

## Poloniex

交易所代码：poloniex

* 用contract查询订单信息仅支持以下**3种**状态：pending, part-deal-pending, active
* 单个交易对支持最近**1天**的成交记录
* OTSDealtTrans:
    * commission_currency: 没有
    * taker/maker: 没有
* get_order: 除了调用single call的get_order还要在open_orders里找

## Quoinex

交易所代码: quoinex
* 由于交易所严格限制请求次数，OneToken会缓存账户信息和下单信息**5秒**。
* 单个交易对支持最近**1000条**的成交记录
* 有原生trans接口: 有(但不能用)
* order list: 不需要contract参数
* cancel all: 不需要contract参数
* trans list: 不需要contract参数
* OTSDealtTrans:
    * 没有commission_currency
* get_trans_list：获得的信息比较少，没有手续费等信息，所以不用get_trans，用get_order_list转换得到
* get_order_list：state支持pending, part-deal-pending, dealt, part-deal-withdrawn, withdrawn
    
## Bibox
交易所代码： bibox
* 没有原生trans接口
* open orders: 不支持avg_dealt_price，值为None
* OTSDealtTans:
    * commission_currency: 没有
    * taker/maker: 没有

## Btcc
交易所代码： btcc
* 有原生trans接口: 没有
* order list: 
    * open orders 不需要contract参数
    * all orders 需要contract参数
* OTSDealtTrans:
    * commission: 没有
    * commission_currency: 没有
    * exchange_tid: 没有
    * dealt_time: 没有
    * taker/maker: 没有
    
## Dextop
交易所代码： dextop
* OTSDealtTrans:
    * commission_currency: 没有
    * exchange_tid: 没有
