
# Official Documentation 1Token APIs and Streams.

### 初次使用

请先阅读[通过网页完成交易](https://1token.trade/r/docs#/getting-started/website-user)。该小节对以下几点进行了说明：

1. 如何在其他交易所生成`api-key`，`api-secret`

2. 如何将上一步生成的`api-key`和`api-secret`导入1token，从而可以通过1token进行交易

3. 1token交易界面主要元素介绍


### API用户

如果用户想要通过API连接1Token并完成相关操作, 请参考[API用户入门指南](https://1token.trade/r/docs#/getting-started/api-user)。该小节讲述了以下内容：

1. 如何在1token生成用于api操作的`ot-key`和`ot-secret`

2. onetoken SDK的安装（目前仅支持`Python 3.6+`，其他语言正在开发中...）

3. 通过运行样例来初步了解SDK中quote和account相关功能


通过api，用户可以拿到基本的信息，比如交易所列表，交易所的contract信息等。通过Websocket API（[websocket API教程](/api-refer/ws-api)）可以订阅逐笔和tick。通过Rest API（[Rest API教程](/api-refer/rest-api)）可以进行下单等交易操作。


__注意__: 1token提供的API是__语言无关__的，可以通过任何支持网络访问的编程语言来使用API。SDK在API上做了一层包装，使得用户可以更加轻松快速地入手，将注意力更多地放在交易本身，而不用过多关注API的细节。1token用`Python`实现了一套强壮完善的SDK，其他语言正在开发中。


### 详细的API说明

对于想自己直接对接API的用户，1token提供有关API的详细swagger说明，用户可以按需查阅：

* [Swagger Basic API](https://1token.trade/r/swagger?url=/r/swagger/basic.yml)
* [Swagger Quote API](https://1token.trade/r/swagger?url=/r/swagger/quote.yml)
* [Swagger Trade API](https://1token.trade/r/swagger?url=/r/swagger/trade.yml)

在直接查阅详细API之前，推荐先阅读[API Reference](/api-refer/rest-api)这一小节，大致了解一下基本信息、行情API、交易加密方式、交易API、历史数据API，之后的API对接会更加容易上手。

### 历史数据(tick)

1token提供历史行情的下载，具体教程请查看[历史数据](https://1token.trade/r/docs#/more/historical-data)一节。