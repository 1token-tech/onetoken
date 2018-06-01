# RESTful API

1Token 所有的API(包括websocket和REST) 都是以下面这两个前缀之一开头的, 这两个前缀提供完全一致的API接口, 唯一的区别是一个是直连香港阿里云, 一个是通过cloudflare的CDN

您可以选择不同的前缀来满足您不同的需求, 举个例子, 如果您的服务器在国内, 我们推荐您使用 `https://1token.trade/api/v1/` 来通过CDN连接 1Token 这样可以避免网络的抖动. 如果您的服务器在海外, 而且直连香港阿里云比较稳定, 我们推荐您使用 `https://api.1token.trade/v1/` 来直接连接1Token
  
  * `https://api.1token.trade/v1/`  (direct to aliyun)  
  * `https://1token.trade/api/v1/`  (through cloudflare CDN)

### API 的详细swagger说明请参考
* [Swagger Basic API](https://1token.trade/r/swagger?url=/r/swagger/quote.yml)
* [Swagger Quote API](https://1token.trade/r/swagger?url=/r/swagger/quote.yml)
* [Swagger Trade API](https://1token.trade/r/swagger?url=/r/swagger/trade.yml)

## 基本信息

基本信息的api可以拿到所有的交易所列表

以及一个交易所的所有的支持交易对（contract）的列表

交易对的信息包括
* min_change 价格跳动的最小单位
* min_amount 下单的最小单位
* min_notional 下单的最小资产 （ price * amount )
* symbol 交易对的唯一标示  ${exchange}/${currency}.${underlying}

详细api请参考 [基本信息API](https://1token.trade/r/swagger?url=/r/swagger/basic.yml)


## 行情API

行情API支持rest的方式去获取最新的行情信息

* 各个交易所历史的candle
* 各个交易所 各个交易对历史逐笔
* 单个交易所当前的tick
* 单个交易所单个合约当前的tick

API的详细介绍 请参考 [行情 Swagger API](https://1token.trade/r/swagger?url=/r/swagger/quote.yml)



## 交易加密方式

#### OT-API/KEY 加密方式

Authentication is done by sending the following HTTP headers:

`Api-Nonce`: A value that should increase between the bounds of 0 and 2^53

`Api-Key`: Your OT-KEY

`Api-Signature`: A signature of the request you are making. It is calculated as `hex(HMAC_SHA256(ot_secret, verb + path + nonce + data))`.

The `data` part of the HMAC construction should be same with the raw body you send to the server. And just be sure that the keys of the data should be sorted.

### Code sample

Python sample code as following:

```python
ot_key = ''
ot_secret = ''

verb = 'POST'
path = '/huobip/test/orders'
nonce = str(int(time.time() * 1000000))
data = {"contract":"huobip/btc.usdt","price":7800.2,"bs":"b","amount":0.6}

if data is None:
    data_str = ''
else:
    assert isinstance(data, dict)
    data_str = json.dumps(data)

parsed_url = urllib.parse.urlparse(path)
parsed_path = parsed_url.path

message = verb + path + str(nonce) + data_str
signature = hmac.new(bytes(ot_secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

# TODO add requests.send() example

```

### Troubleshooting

* If there is a request body, make sure your `Content-Type` set to `application/json`.


## 交易API


通过交易API 您可以

* 获取到交易所某个账号的余额
* 获取到交易所某个账号的持仓信息
* 对某个交易所 某个合约进行下单
* 对已经下去的某个订单进行撤单
* 获取某个账号的充值地址
* 对某个账号进行提现


详情请参考 [交易 Swagger API](https://1token.trade/r/swagger?url=/r/swagger/trade.yml)


## 历史数据API

你可以通过API去下载所有的历史tick行情
[Hist Quote](more/historical-data)
