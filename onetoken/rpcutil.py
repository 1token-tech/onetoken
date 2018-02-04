class Const:
    SUCCESS = 'SUCCESS'
    EXCHNAGE_ERROR = 'EXCHANGE_ERROR'  # 访问远程的服务器返回500 或者另外一些意想不到的错误
    EXCHANGE_TIMEOUT = 'EXCHANGE_TIMEOUT'  # 访问远程服务器 timeout
    LOGIC_ERROR = 'LOGIC_ERROR'  # 下单价格不对。 下单钱不够 订单号不存在等


class ServiceError(Exception):
    def __init__(self, code, message=''):
        self.code = code
        self.message = message

    def __str__(self):
        return 'ServiceError<{},{}>'.format(self.code, self.message)


class HTTPError(ServiceError):
    TIMEOUT = 'TIMEOUT'  # timeout
    RESPONSE_5XX = 'RESPONSE_5XX'  # 服务器返回5xx错误
    RESPONSE_4XX = 'RESPONSE_4XX'  # 服务器返回4xx错误
    NOT_200 = 'NOT_200'  # 服务器返回4xx错误
    NOT_JSON = 'NOT_JSON'  # 不是 json 格式
    HTTP_ERROR = 'HTTP_ERROR'  # client 出错

    def __init__(self, code, message=''):
        self.code = code
        self.message = message

    def __str__(self):
        return 'HTTPError<{},{}>'.format(self.code, self.message)


class Code:
    CLIENT_OID = None
    EXCHANGE_OID = None
    CLIENT_CANCEL = None
    CONTRACT_NOT_EXIST = None
    NOT_200 = None
    NOT_JSON = None
    TIMEOUT = None
    WEBSOCKET_UNHEALTH = None
    ACCOUNT_WAITTING_CREATE = None
    ACCOUNT_NOT_EXIST = None
    SUCCESS = None
    WEBSOCKET_CONNECTING = None
    ACCOUNT_TOO_FREQUENT = None
    SOME_ERROR = None
    UNEXPECT_ERROR = None
    UNKNOW_METHOD = None
    NO_PERMISSION = None


def set_code():
    for k in Code.__dict__:
        import re
        if re.match('^[A-Z_]*$', k):
            setattr(Code, k, k)


set_code()
