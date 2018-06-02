
# 1token使用指南

### 1token可以做什么？

现在市面上有很多数字货币的交易所，一些交易者想要在多个交易所进行交易，因此需要自行管理多家交易所的账号，编写不同的程序去对接不同交易所的API————这对任何个人和机构来说都不算一件轻松愉快的事。

1token将不同交易所的API进行整理和封装，提供给用户一套统一的API。用户使用1token提供的统一API，以及对应的[交易所标识](/exchange-overview?#支持的交易所)就可在对应交易所进行交易。

举例来说，Abo是一个数字货币的交易者，他想在AA和BB这两个交易所做跨交易所套利。

* __不使用1token__: Abo需要编写两个程序来分别实现与AA和BB两个交易所API的对接，或是在AA和BB的网站之间切换以进行交易。

* __使用1token__：Abo在1token完成相应账户设置之后，只需实现与1token API的对接（或使用1token提供的SDK），或是直接在1token网站内即可完成AA和BB两个交易所的交易。

__交易者涉及的交易所越多，1token的优势越明显。__

1token将交易者从繁杂的多交易所账号管理和API对接之中解放出来，帮助交易者将更多的精力集中于交易本身。

### 初次使用

请先阅读[通过网页完成交易](/getting-started/website-user)。该小节对以下几点进行了说明：

1. 如何在其他交易所生成`api-key`，`api-secret`

2. 如何将上一步生成的`api-key`和`api-secret`导入1token，从而可以通过1token进行交易

3. 1token交易界面主要元素介绍


### API用户

如果用户想要通过API连接1Token并完成相关操作, 请参考[API用户入门指南](/getting-started/api-user)。该小节讲述了以下内容：

1. 如何在1token生成用于api操作的`ot-key`和`ot-secret`

2. onetoken SDK的安装（目前仅支持`Python 3.6+`，其他语言正在开发中...）

3. 通过运行样例来初步了解SDK中quote和account相关功能


通过api，用户可以拿到基本的信息，比如交易所列表，交易所的contract信息等。其中，通过Websocket API（[websocket API教程](/api-refer/ws-api)）来订阅逐笔和tick；通过Rest API（[Rest API教程](/api-refer/rest-api)）来进行下单等交易操作。


__注意__: 1token提供的API是__语言无关__的，可以通过任何支持网络访问的编程语言来使用API。SDK在API上做了一层包装，使得用户可以更加轻松快速地入手，将注意力更多地放在交易本身，而不用过多关注API的细节。1token用`Python`实现了一套强壮完善的SDK，其他语言的正在开发中。


### 详细的API说明

对于想自己直接对接API的用户，1token提供有关API的详细swagger说明，用户可以按需查阅：

* [Swagger Basic API](https://1token.trade/r/swagger?url=/r/swagger/basic.yml)
* [Swagger Quote API](https://1token.trade/r/swagger?url=/r/swagger/quote.yml)
* [Swagger Trade API](https://1token.trade/r/swagger?url=/r/swagger/trade.yml)

在直接查阅详细API之前，推荐先阅读[API Reference](/api-refer/rest-api)这一小节，大致了解[基本信息](/api-refer/rest-api#基本信息)、[行情API](/api-refer/rest-api#行情API)、[交易加密方式](/api-refer/rest-api#交易加密方式)、[交易API](/api-refer/rest-api#交易API)、[历史数据API](/api-refer/rest-api#历史数据API)，之后的API对接会更加容易上手。

### 历史数据(tick)

1token提供历史行情的下载，具体教程请查看[历史数据](/more/historical-data)一节。