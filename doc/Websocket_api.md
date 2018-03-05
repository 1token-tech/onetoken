Websocket
====
Btp Websocket Api doc

General
--
Connect your websocket client to `wss://api.qbtrade.org/quote/ws`

A basic command is sent in the following format:
```$xslt
{
    'uri': '<command>',
    'args': {'arg1':'value1', 'arg2':'value2', ...}
}
```
The following commands are available without authentication:
* `subscribe-single-tick-verbose` subscribe a real-time ticker info of a given contract 
###Subscribe
Subscribe ticker
```$xslt
//request
{
    'uri': 'subscribe-single-tick-verbose', 
    'args': {'contract': '<contract>'}
}
```
###Heartbeat
```     
//webSocket Client request
{
    'uri': 'ping'
}

//webSocket Server response
{
    'uri': 'pong'
} 
```

