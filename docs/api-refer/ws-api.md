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
逐笔与tick数据支持订阅后退订，示例如下：
```
//Websocket Client request
{
    "uri": "unsubscribe-single-tick-verbose",
    "contract": "bitfinex/btc.usd"
}
```
或：
```
//Websocket Client request
{
    "uri": "unsubscribe-single-zhubi-verbose",
    "contract": "bitfinex/btc.usd"
}
```


### 实时candle数据接口
推送各个交易所的实时candle数据。

地址: `wss://1token.trade/api/v1/ws/candle`

支持不同时长：1m,5m,15m,30m,1h,2h,4h,6h,1d,1w。

支持同一连接订阅多个合约。请求示例如下：

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

地址 `wss://1token.trade/api/v1/ws/low-freq-quote-v2`

支持同时订阅不同交易所的不同合约：
```
//Websocket Client request
{
    "uri":"batch-subscribe",
    "contracts":["huobip/btc.usdt", "huobip/ht.usdt"]
}

//Websocket Server response
{
    "uri":"batch-subscribe",
    "code":"success"
}

//Websocket Server response
{
    "uri":"low-freq-quote",
    "data":
    [
        {
            "contract":"huobip/btc.usdt", 
            "rise":3.345103,
            "price":6152.32,
            "price_s":"6152.32"         //根据交易所的min_change format的字符串
        },
        {
            "contract":"huobip/ht.usdt", 
            "rise":-0.539916,
            "price":3.7027,
            "price_s":"3.7027"
        }
    ]
}
```
其中，rise的单位为百分比，同时推送float64以及string类型的当前价格（price）。

支持订阅后退订，示例如下：
```
//Websocket Client request
{
    "uri":"batch-unsubscribe",
    "contracts":["huobip/btc.usdt", "huobip/ht.usdt"]
}

//Websocket Server response
{
    "uri":"batch-unsubscribe",
    "code": "success"
}
```

### 实时tick-v3行情 （Alpha）
推送v3格式的tick行情，每隔30秒服务器会推送snapshot，在此间隔内发送diff，客户端可以通过计算snapshot+diff得出当前行情。

在diff类型的数据中，如bids或者asks中存在[x,y=0]的情况，则删除上个snapshot中bids或asks价格为x的行情，否则更新此行情。

地址 `wss://1token.trade/api/v1/ws/tick-v3`

该接口默认采用gZip压缩数据发送至客户端，客户端首先需要发送auth进行认证：
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

接口支持同时订阅不同交易所的不同合约，示例如下：

```
//Websocket Client request
{
    "uri":"subscribe-single-tick-verbose","contract":"huobip/btc.usdt"
}

//Websocket Server response(snapshot)
 {
     "tp":"s",                      //type: snapshot
     "ui":16222,                    //update_id: 16222
     "tm":1527401596.654875,        //time
     "et":1527401596.511            //exchange_time
     "c":"huobip/btc.usdt",         //contract
     "l":7291.79,                   //last
     "v":0,                         //volume
     "b":                           //bids
     [
        [7291.97,1],                //[price, volume]
        ...
        [7232.65,0.1155]
     ],
     "a":                           //asks
     [
        [7292.51,0.001],
        ...
        [7455.15,0.1]
     ]
}

//Websocket Server response(diff)
{
    "tp":"d",                       //type: diff
    "ui":16223,
    "tm":1527401598.138354,
    "et":1527401598.013,
    "c":"huobip/btc.usdt",
    "l":7291.97,
    "v":0,
    "b":
    [
        [7291.97,0.8298],
        ...,
        [7232.65,0]
    ],
    "a":
    [
        [7297.19,0.2],
        ...,
        [7455.15,0]
    ]
}
```