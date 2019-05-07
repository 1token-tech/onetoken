
1Token的API是语言无关的, 您可以使用各类语言接入1Token

如果您希望自己封装对1Token的接口 可以参考当前这个项目, 来帮助您更快速的对接1Token

这个repo包含了Python Java的简单demo, 包括如何获取简单的行情, 如何查询一个交易账户的信息, 如何下单撤单. 如果需要更详细的文档和帮助 请参考
https://1token.trade/docs 和 https://1token.trade/swagger

如果您需要更完整的SDK, 可以使用以下几个项目
## Python

### 同步SDK

适合所有python使用者, 基于[requests](https://github.com/kennethreitz/requests)

https://github.com/1token-trade/onetoken-py-sdk-sync

### 异步SDK

适合有经验的python使用者, 用异步sdk需要掌握python的[asyncio](https://docs.python.org/3/library/asyncio.html)语法

这个sdk基于[aiohttp](https://github.com/aio-libs/aiohttp)和python3.6+ 开发

https://github.com/1token-trade/onetoken-py-sdk


## Golang

https://github.com/1token-trade/onetoken-go-sdk


## C++

https://github.com/1token-trade/onetoken-ctp