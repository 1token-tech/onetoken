
# 错误码

## OTS错误码

|错误代码|解释|
|:---|---|
|invalid-white-list|`错误的白名单 ip, ots 并不支持的 ip`|
|invalid-jwt|  `错误的用户 jwt`|
|invalid-api-key|  `错误用户 ot-key, ot-secret`|
|no-valid-authentication|  `无可用的用户认证(jwt 或 api_key)`|
|no-permission | `无权限访问`|
|not-allowed | `有权限但当前资源不可用`|
|partial-success | `batch operations 部分成功`|
|unexpected-error  |`ots 系统内部错误`|
|invalid-param | `错误的 ots 的参数`|
|client_oid-not-found | `指定的 client order id 不存在`|
|client_oid-already-existed | `指定的 client order id 已经存在`|
|exchange_oid-not-found|  `指定的 exchange order id 不存在，或根据 client order id 没有找到对应的 exchange order id`|
|client_wid-not-found|  `指定的 client withdraw id 不存在`|
|client_wid-already-existed|  `指定的 client withdraw id 已经存在`|
|exchange_wid-not-found|  `指定的 exchange withdraw id 不存在，或根据 client withdraw id 没有找到对应的 exchange withdraw id`|
|contract-not-exist|  `指定的 contract 不存在或不可用`|
|invalid-account-config|  `错误的 account config`|
|wait-for-initializing | `等待账户后台初始化`|
|upstream-error|  `上层ot服务不可用`|
|no-available-proxy|  `无可用 proxy-ip 出口`|
|proxy-ip-banned|  `proxy-ip 已经被暂时禁用`|
|proxy-connect-fail | `连接 proxy 失败`|

## 第三方交易所相关的错误码

|错误代码|解释|
|:---|---|
|rate-limit-exceeded|  `请求超出交易所限制`|
|invalid-exg-param|  `交易所接受参数错误`|
|unexpected-data-format | `交易所返回错误的数据格式`|
|place-order-no-money| `账户资金不足`|
|place-order-min-notional | `账户下单金额低于交易所最低限制`|
|place-order-error-amount | `账户下单数量错误`|
|place-order-error-price | `账户下单价格错误`|
|cancel-order-not-exist | `订单已被撤销或订单不存在`|
|undefined-exg-error | `还没有及时被 ot 系统 handle 的错误`|
|timeout | `访问交易所超时`|
|unknown-exg-error| `交易所系统错误, 状态不明`|
|bad-gateway|  `交易所 bad-gateway`|


