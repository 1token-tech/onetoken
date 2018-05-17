## 安装

### Python
* 系统需求 Python 3.6+

* 用户可以通过```pip```获取onetoken

    ```shell
    pip install onetoken -U
    ```

* 在Python脚本中导入onetoken

    ```Python
    import onetoken as ot
    print(ot.__version__)
    ```


## 使用

* 运行Account示例程序前需要准备好OneToken的api_key和api_secret

    * 用户请访问[OneToken官网](https://1token.trade/)，按照[新手指引](https://1token.trade/r/ot-guide/index)注册账号，获取api_key和api_secret


* 用户可以在自己开发的Python程序中导入onetoken模块

    ```python
    import onetoken as ot
    ```

* 下载OneToken示例程序:

    ```shell
    git clone git@github.com:qbtrade/onetoken.git
    ```

* 运行示例程序`quote.py`获取行情Tick:

    `$ python quote.py`

* 运行示例程序`account.py`:

    `$ python account.py`

    根据命令行提示输入OneToken的api_key和api_secret。程序运行后会在控制台输出用户在交易所的账户信息，拥有的比特币数量和当前未成交的订单列表。

    用户初次使用账户时程序可能返回**Acc is initializing, please try later.**错误，过2秒重试即可。
