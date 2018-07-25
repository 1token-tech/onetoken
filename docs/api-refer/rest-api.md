# RESTful API

1Token 所有的API(包括websocket和REST) 都是以`https://1token.trade/api/v1/` 开头的


### API 的详细swagger说明请参考
* [Swagger Basic API](https://1token.trade/swagger?url=/swagger/quote.yml)
* [Swagger Quote API](https://1token.trade/swagger?url=/swagger/quote.yml)
* [Swagger Trade API](https://1token.trade/swagger?url=/swagger/trade.yml)

## 基本信息

基本信息的api可以拿到所有的交易所列表

以及一个交易所的所有的支持交易对（contract）的列表

交易对的信息包括
* min_change 价格跳动的最小单位
* min_amount 下单的最小单位
* min_notional 下单的最小资产 （ price * amount )
* symbol 交易对的唯一标示  ${exchange}/${currency}.${underlying}

详细api请参考 [基本信息API](https://1token.trade/swagger?url=/r/swagger/basic.yml)


## 行情API

行情API支持rest的方式去获取最新的行情信息

* 各个交易所历史的candle
* 各个交易所 各个交易对历史逐笔
* 单个交易所当前的tick
* 单个交易所单个合约当前的tick

API的详细介绍 请参考 [行情 Swagger API](https://1token.trade/swagger?url=/swagger/quote.yml)



## 交易加密方式

#### OT-API/KEY 加密方式
<!-- 
Authentication is done by sending the following HTTP headers:

`Api-Nonce`: A value that should increase between the bounds of 0 and 2^53

`Api-Key`: Your OT-KEY

`Api-Signature`: A signature of the request you are making. It is calculated as `hex(HMAC_SHA256(ot_secret, verb + path + nonce + data))`.

The `data` part of the HMAC construction should be same with the raw body you send to the server. And just be sure that the keys of the data should be sorted. -->

用API来交易时需要在请求的`HTTP header`中加入以下内容以完成__身份验证__：

|key|value|
|---|---|
|`Api-Nonce`|一个在0到2^53大小范围内增加的值|
|`Api-Key`|在1token生成的`OT-KEY`（若没有，请参考[生成OT_KEY](/getting-started/api-user#通过API来进行交易)）|
|`Api-Signature`|本次请求的签名，计算方法为<br/>`hex(HMAC_SHA256(ot_secret, verb + path + nonce + data))`|

`Api-Signature`计算公式中的`data`应与本次请求发送到服务器的`raw body`相同，`data`在stringfy时不要求按key排序。

### 代码示例

Python例程:

```python
import time
import json
import urllib.parse
import hmac
import hashlib
import requests

# 填入你的ot_key
ot_key = ''
# 填入你的ot_secret
ot_secret = ''

def gen_nonce():
    return str((int(time.time() * 1000000)))


def gen_headers(nonce, key, sig):
    headers = {
        'Api-Nonce': nonce,
        'Api-Key': key,
        'Api-Signature': sig,
        'Content-Type': 'application/json'
    }
    return headers


def gen_sign(secret, verb, path, nonce, data=None):
    if data is None:
        data_str = ''
    else:
        assert isinstance(data, dict)
        # server并不要求data_str按key排序，只需此处用来签名的data_str和所发送请求中的data相同即可，是否排序请按实际情况选择
        data_str = json.dumps(data, sort_keys=True)
    parsed_url = urllib.parse.urlparse(path)
    parsed_path = parsed_url.path

    message = verb + parsed_path + str(nonce) + data_str
    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    print('nonce:', nonce)
    print('parsed_path:', parsed_path)
    print('data_str:', data_str)
    print('message:', message)
    return signature


def place_order():
    verb = 'POST'

    # 下单的api前缀如下，具体请查看1token API文档
    url = 'https://1token.trade/api/v1/trade'

    # path的具体构成方法请查看1token API文档
    path = '/huobip/zannb/orders'

    nonce = gen_nonce()
    data = {"contract": "huobip/btc.usdt", "price": 1, "bs": "b", "amount": 0.6}
    sig = gen_sign(ot_secret, verb, path, nonce, data)
    headers = gen_headers(nonce, ot_key, sig)
    # server并不要求请求中的data按key排序，只需所发送请求中的data与用来签名的data_str和相同即可，是否排序请按实际情况选择
    resp = requests.post(url + path, headers=headers, data=json.dumps(data, sort_keys=True))
    print(resp.json())


def get_info():
    verb = 'GET'
    url = 'https://1token.trade/api/v1/trade'
    path = '/huobip/zannb/info'
    nonce = gen_nonce()
    sig = gen_sign(ot_secret, verb, path, nonce)
    headers = gen_headers(nonce, ot_key, sig)
    resp = requests.get(url + path, headers=headers)
    print(resp.json())


def main():
    place_order()
    get_info()


if __name__ == '__main__':
    main()

```

### 遇到了问题？

<!-- * If there is a request body, make sure your `Content-Type` set to `application/json`. -->
* 如果本次请求包含`body`，请确保将`Content-Type`设置为`application/json`。


## 交易API


通过交易API 您可以

* 获取到交易所某个账号的余额
* 获取到交易所某个账号的持仓信息
* 对某个交易所 某个合约进行下单
* 对已经下去的某个订单进行撤单
* 获取某个账号的充值地址
* 对某个账号进行提现


详情请参考 [交易 Swagger API](https://1token.trade/swagger?url=/swagger/trade.yml)


## 历史数据API

你可以通过API去下载所有的历史tick行情
[Hist Quote](more/historical-data)
