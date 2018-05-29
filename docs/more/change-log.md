### 2018-05-27
* The realtime candle websocket service now support multi subscribe in one connection
* Add tick-v3 websocket service readme(Alpha)

### 2018-05-25
* Websocket server will shut down the connection if ping message didn't receive in 30s

### 2018-05-23

* Websocket add gzip=true endpoint, you can use ```wss://1token.trade/api/v1/ws/tick?gzip=true``` to get gzipped websocket
* non gzip websockets will be deprecated

### 2018-05-14

* Websocket start use new endpoint prefix ```wss://1token.trade/api/v1/ws``` and ```wss://api.1token.trade/v1/ws```
