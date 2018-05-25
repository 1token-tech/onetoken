# Websocket API

### 简介
实时行情，推送包括实时candle，24小时涨跌幅数据，tick以及逐笔数据，以Json格式发送并接受请求。如：
```
{
    "uri":"",
    "command":""
}
```

所有接口支持心跳方式检测服务器是否在线，心跳时长为30秒。若客户端超过30秒未发送心跳包，服务端会返回丢失心跳的通知，并主动断开该连接。示例如下：
```  
//Websocket Client request
{
    "uri": "ping"
}

//Websocket Server response
{
    "uri": "pong",
    "timestamp": 1526357597.237
} 
```

同时支持UUID字段以标示不同连接(服务端返回相同UUID)，如：
```    
//Websocket Client request
{
    "uri": "ping",
    "uuid": "this-is-a-uuid"
}

//Websocket Server response
{
    "uri": "pong",
    "uuid": "this-is-a-uuid",
    "timestamp": 1526357597.237
} 
```

所有Websocket接口支持服务端发送gZip格式数据，是否使用gZip以各Websocket的地址参数为准。如`wss://1token.trade/api/v1/ws/tick?gzip=true` 则表明使用gZip压缩传输数据。

注意：除tick-v3行情Websocket接口，在用户没用指明是否使用gZip的情况下，其它接口均默认不使用gZip压缩数据传输。



### 实时tick、逐笔交易数据接口
推送各交易所的tick、逐笔交易数据。

地址 `wss://1token.trade/api/v1/ws/tick`

支持同时订阅不同交易所的不同合约，首先需要发送auth进行认证：
```
//Websocket Client request
{
    "uri":"auth"
}

//Websocket Server response
{
    "uri":"auth",
    "message":"Auth succeed."
}
```

订阅逐笔数据：
```
//Websocket Client request
{
    "uri": "subscribe-single-zhubi-verbose",
    "contract": "bitfinex/btc.usd"
}

//Websocket Server response
{
    "uri":"single-zhubi-verbose",
    "data":
    [
        {
            "amount": 0.21,
            "bs": "s",
            "contract": "bitfinex/btc.usd",
            "exchange_time": "2018-05-03T08:14:20.307000+00:00",
            "price": 9231.8,
            "time": "2018-05-03T16:14:20.541068+08:00"
        }
    ]
}
```

订阅tick数据：
```
//Websocket Client request
{
    "uri": "subscribe-single-tick-verbose",
    "contract": "bitfinex/btc.usd"
}

//Websocket Server response
{
    "uri":"single-tick-verbose",
    "data":
    {
         "asks":
         [
             {"price": 9218.5, "volume": 1.7371},
             ...
         ],
         "bids":
         [
             {"price": 9218.4, "volume": 0.81871728},
             ...
         ],
         "contract": "bitfinex/btc.usd",
         "last": 9219.3,  // 最新成交价
         "time": "2018-05-03T16:16:41.630400+08:00",  // 1token的系统时间 ISO 格式 带时区
         "exchange_time": "2018-05-03T16:16:41.450400+08:00",  // 交易所给的时间 ISO 格式 带时区
         "amount": 16592.4,  //成交额 (CNY)
         "volume": 0.3   // 成交量
   }
}
```

### 实时candle数据接口
推送各个交易所的实时candle数据。

地址: `wss://1token.trade/api/v1/ws/candle`

支持不同时长：1m,5m,15m,30m,1h,2h,4h,6h,1d,1w。

如需同时推送多个时长candle，请建立多个连接进行请求。请求示例如下：

```
//Websocket Client request
{
    "contract":"huobip/btc.usdt", 
    "duration": "1m"
}

//Websocket Server response
{
    "amount": 16592.4, //成交量
    "close": 9220.11,
    "high": 9221,
    "low": 9220.07,
    "open": 9220.07,
    "volume": 0.3, //成交额
    "contract": "huobip/btc.usdt",
    "duration": "1m",
    "time": "2018-05-03T07:30:00Z" // 时间戳 isoformat
} 
```

### 24小时涨跌幅数据接口
推送各个合约的当前价格以及24小时涨跌幅。

地址 `wss://1token.trade/api/v1/ws/low-freq-quote`

支持同时订阅不同交易所的不同合约：
```
//Websocket Client request
{
    "uri":"subscribe",
    "contract":"huobip/btc.usdt"
}


//Websocket Server response
{
    "contract":"huobip/btc.usdt", 
    "rise": 1.919558,
    "price": 8754.89,
    "price_s": "8754.89" //根据交易所的min_change format的字符串
}
```
其中，rise的单位为百分比，同时推送float64以及string类型的当前价格（price）。

