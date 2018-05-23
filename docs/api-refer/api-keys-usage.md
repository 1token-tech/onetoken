API Keys Usage
====

Authenticating with an API Key
---
Authentication is done by sending the following HTTP headers:

`Api-Nonce`: A value that should increase between the bounds of 0 and 2^53

`Api-Key`: Your **onetoken** public API key.

`Api-Signature`: A signature of the request you are making. It is calculated as `hex(HMAC_SHA256(apiSecret, verb + path + nonce + data))`.

### 'data'
The `data` part of the HMAC construction should be same with the raw body you send to the server. And just be sure that the keys of the data should be sorted.
 
### Code sample

```python
ot_key = ''
ot_secret = ''

#
# POST
#
verb = 'POST'
path = '/huobip/test/orders'
nonce = str(int(time.time() * 1000000))
data = {"contract":"huobip/btc.usdt","price":7800.2,"bs":"b","amount":0.6}


if data is None:
    data_str = ''
else:
    assert isinstance(data, dict)
    data_str = json.dumps(data, sort_keys=True)

parsed_url = urllib.parse.urlparse(path)
parsed_path = parsed_url.path

# print(message)
message = verb + path + str(nonce) + data_str

# print "Computing HMAC: %s" % verb + path + str(nonce) + data
signature = hmac.new(bytes(ot_secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

```

### Troubleshooting

* If there is a request body, make sure your `Content-Type` set to `application/json`.
