
# 通过API来进行交易

### 1. 创建 ot key 和 ot secret，请务必保管好新建的 ot key 和 ot secret

![step1](https://1token.trade/oss/web/guide2/pic1.jpg)

### 2. 设置添加账号并且设置 api key

![step1](https://1token.trade/oss/web/guide2/pic2.jpg)

此步骤配置您在交易网站(如 huobi.com)上的账号和设置好的 api key 和 api secret 您也可以使用模拟账号跑样例，模拟账号不需要设置交易的 api key 和 api secret

![step1](https://1token.trade/oss/web/guide2/pic3.jpg)

### 3. 下载onetoken SDK
```shell
  git clone git@github.com:qbtrade/onetoken.git
```



### 4. 执行 quote 样例

进入 onetoken 目录，命令行中运行命令 `python examples/quote.py`

![step1](https://1token.trade/oss/web/guide2/pic4.jpg)

看到类似以下输出说明 quote 连接成功
![step1](https://1token.trade/oss/web/guide2/pic5.jpg)


### 5. 执行 account 样例

进入 onetoken 目录，命令行中运行命令 `python examples/account.py`

![step1](https://1token.trade/oss/web/guide2/pic6.jpg)

依次输入步骤 1 添加的 ot key 和 ot secret，以及步骤 2 添加的账号，账号格式为”平台英文 标识符/账号”，如火币平台的账号 yojhop 则为 huobip/yojhop。常用平台英文标识符如下:

|交易平台|平台标识符|
|---|---|
| 火币|huobip |
| okex|okex|
| 币安|binance|
| bitflyer|bitflyer|
| bithumb|bithumb|
| quoinex|quoinex|
| okef|okef|
| 模拟|mock|

看到如下输出说明样例执行成功:


![step1](https://1token.trade/oss/web/guide2/pic7.jpg)
