# Getting Started

## Normal User

### 第一步 点击注册

![step1](https://1token.trade/oss/web/guide/guide1.jpg)

### 第二步 填写信息 完成注册

![step2](https://1token.trade/oss/web/guide/guide2.jpg)

### 第三步 登录交易所，点击API管理 （以火币为例）

![step4](https://1token.trade/oss/web/guide/guide4.jpg)

### 第四步 设置API备注，创建API

![step5](https://1token.trade/oss/web/guide/guide5.jpg)

### 第五步 保存访问密匙和私密密匙

![step6](https://1token.trade/oss/web/guide/guide6.jpg)

### 第六步 进入用户中心，选择交易所并设置账号名。

![step3](https://1token.trade/oss/web/guide/guide3.jpg)

### 第七步 输入密匙与私匙，添加API，进入币币交易界面。

![step7](https://1token.trade/oss/web/guide/guide7.jpg)

### 第八步 进入币币交易界面进行交易

![step8](https://1token.trade/oss/web/guide/eightStep.jpg)

## API User

### 创建 ot key 和 ot secret，请务必保管好新建的 ot key 和 ot secret

![step1](https://1token.trade/oss/web/guide2/pic1.jpg)

### 设置添加账号并且设置 api key

![step1](https://1token.trade/oss/web/guide2/pic2.jpg)

* 此步骤配置您在交易网站(如 huobi.com)上的账号和设置好的 api key 和 api secret 您也可以使用模拟账号跑样例，模拟账号不需要设置交易的 api key 和 api secret

![step1](https://1token.trade/oss/web/guide2/pic3.jpg)


### 执行 quote 样例，进入 onetoken 目录，命令行中运行命令 python examples/quote.py

![step1](https://1token.trade/oss/web/guide2/pic4.jpg)

* 看到类似以下输出说明 quote 连接成功
![step1](https://1token.trade/oss/web/guide2/pic5.jpg)


### 执行 account 样例，进入 onetoken 目录，命令行中运行命令 python examples/account.py

![step1](https://1token.trade/oss/web/guide2/pic6.jpg)

依次输入步骤 1 添加的 ot key 和 ot secret，以及步骤 2 添加的账号，账号格式为”平台英文 标识符/账号”，如火币平台的账号 yojhop 则为 huobip/yojhop。常用平台英文标识符如下:

* 火币:huobip 
* okex:okex
* 币安:binance
* bitflyer:bitflyer
* bithumb:bithumb
* quoinex:quoinex
* okef:okef
* 模拟:mock

看到如下输出说明样例执行成功:


![step1](https://1token.trade/oss/web/guide2/pic7.jpg)
