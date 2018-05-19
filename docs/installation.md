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

    * 用户请访问[OneToken官网](https://1token.trade/)，按照[新手指引](https://1token.trade/r/docs#/getting-started/website-user)注册账号，获取ot_key和ot_secret


* 用户可以在自己开发的Python程序中导入onetoken模块

    ```python
    import onetoken as ot
    ```

* 下载OneToken示例程序:

    ```shell
    git clone https://github.com/1token-trade/onetoken
    ```

<<<<<<< HEAD
* 运行示例程序`examples/quote.py`获取行情Tick:

    `$ python examples/quote.py`

* 运行示例程序`examples/account.py`:

    `$ python examples/account.py`

    根据命令行提示输入OneToken的ot_key和ot_secret。程序运行后会在控制台输出用户在交易所的账户信息，拥有的比特币数量和当前未成交的订单列表。
=======
* 进入onetoken目录：
    ```shell
    cd onetoken
    ```


* 运行示例程序`example/quote.py`获取行情Tick:

    `$ python example/quote.py`

* 运行示例程序`example/account.py`:

    `$ python example/account.py`

    根据命令行提示输入OneToken的`api_key`和`api_secret`。程序运行后会在控制台输出用户在交易所的账户信息，拥有的比特币数量和当前未成交的订单列表。
>>>>>>> update

    用户初次使用账户时程序可能返回`Acc is initializing, please try later.`错误，过2秒重试即可。
