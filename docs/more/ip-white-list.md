# 添加IP白名单

### 给key和secret加保险

推荐在其他交易所生成api-key与api-secret时，将下方所列经认证为1token所持有的ip地址加入该key-secret的白名单，以确保只有1token可以使用该key-secret进行交易。这样，就算key与secret不慎被盗，别人也无法通过白名单之外的设备进行交易，从而更高地保护您的个人财产。

以火币Huobi为例

1.在生成`key`, `secret`时填入1token持有的ip中的一个或多个。如下图中将生成一对专供在1token交易使用的`key`, `secret`，我们将他命名为__1token__，并将下方所列的`47.52.239.19`这个ip填入白名单。

![step1](../img/add-white-list-ip.png)

2.生成并确认

![step2](../img/success.png)

![step3](../img/my-key.png)

这样子就只有通过`47.52.239.19`这个ip发出的交易请求才会被huobi接受，大大增加了个人账户的安全性。

后续的使用请参考[通过1token网页进行交易](..\getting-started\website-user.md)或是[通过1token API进行交易](..\getting-started\api-user.md)。


### 1token持有的ip

- 47.52.239.19
- 47.52.105.31
- 47.52.233.96
- 47.52.243.168
- 47.52.231.159
- 47.91.233.85
- 47.52.75.3
- 47.52.238.85
- 47.91.215.190