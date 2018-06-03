


# 通过API来进行交易

### 1. 创建 ot key 和 ot secret，请务必保管好新建的 ot key 和 ot secret

![step1](../img/101.png)

### 2. 设置添加账号并且设置 api key

请参考 [在1token设置账号和api-key](/getting-started/website-user#第三步-登录交易所，点击api管理-（以火币为例）)

### 3. 安装onetoken SDK 
* 我们目前只提供python的SDK, 不过API是语言无关的, 其他语言也可以使用。安装python的SDK，可以使用如下指令
```shell
pip install onetoken -U
```


### 4. 执行 quote 样例
```
git clone https://github.com/1token-trade/onetoken
```

进入 onetoken 目录，命令行中运行命令 `python examples/quote.py`

![step2](../img/102.png)

看到类似以下输出说明 quote 连接成功
![step3](../img/103.png)


### 5. 执行 account 样例

进入 onetoken 目录，命令行中运行命令 `python examples/account.py`

![step4](../img/104.png)

依次输入步骤 1 添加的 ot key 和 ot secret，以及步骤 2 添加的账号，账号格式为”平台英文 标识符/账号”，如火币平台的账号 zannb 则为 huobip/zannb。常用平台英文标识符如下:

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


![step5](../img/105.png)