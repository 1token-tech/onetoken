const request = require('sync-request')
const crypto=require('crypto')
const url=require('url')
const assert = require('assert')
const readline = require('readline').createInterface({
     input: process.stdin,
     output: process.stdout
   })
  
  
const secret={otKey:'',otSecret:''}
function getHash(secret,message){
	console.log('hash',crypto.createHmac('SHA256', secret).update(message).digest('hex'))
    return crypto.createHmac('SHA256', secret).update(message).digest('hex')
}
function genSign(secret, verb, endpoint, nonce, dataStr){
    if(!dataStr) dataStr=''
    let parsedUrl = url.parse(endpoint)
    path = parsedUrl.path
    message = verb + path + nonce + dataStr
	console.log(message)
    return getHash(secret,message)
}
function apiCall(method, endpoint, params={}, data=null, timeout=15000, host='https://1token.trade/api/v1/trade'){
    method = method.toUpperCase()

    let nonce = genNonce()

    let url = host + endpoint

    let jsonStr = data?JSON.stringify(data):''
    sign = genSign(secret.otSecret, method, endpoint, nonce, jsonStr)
	console.log(secret,method,endpoint,nonce,jsonStr,sign)
    headers = {'Api-Nonce': nonce+'', 'Api-Key': secret.otKey, 'Api-Signature': sign,
               'Content-Type': 'application/json'}
    let options={body:jsonStr,qs:params,headers,timeout}
    res = request(method, url=url, options)
    return res
}
function genNonce(){
    return Date.now() * 1000
}

function demo(account){
    console.log('查看账户信息')
    r = apiCall('GET', `/${account}/info`)
    console.log(r.getBody('utf8'))

    console.log('撤销所有订单')
    r = apiCall('DELETE',`/${account}/orders/all`)
    console.log(r.getBody('utf8'))

    console.log('下单')
    r = apiCall('POST',`/${account}/orders`,{},
                 data={'contract': 'okex/btc.usdt', 'price': 10, 'bs': 'b', 'amount': 1, 'options': {'close': true}})
    console.log(r.getBody('utf8'))
    r=JSON.parse(r.getBody('utf8'))
    assert(r.client_oid)
    let exgOid=r.exchange_oid
	console.log('查询挂单 应该有一个挂单')
	r = apiCall('GET', `/${account}/orders`)
	console.log(r.getBody('utf8'))
	r=JSON.parse(r.getBody('utf8'))
	assert(r.length===1)
	console.log('用 exchange oid撤单')
	r = apiCall('DELETE', `/${account}/orders`, params={exchange_oid: exgOid})
	console.log(r.getBody('utf8'))
	console.log('查询挂单 应该没有挂单')
	r = apiCall('GET', `/${account}/orders`)
	console.log(r.getBody('utf8'))
	r=JSON.parse(r.getBody('utf8'))
	assert(r.length===0)
    

}
function main(){
    readline.question('ot-key: ', otKey => {
        secret.otKey=otKey
        readline.question('ot-secret: ',otSecret=>{
            secret.otSecret=otSecret
            readline.question('请输入交易账号 账号格式是 {交易所}/{交易账户名} 比如 okex/mock-1token: ',account=>{
                readline.close()
                demo(account)
            })
        })
    })
}
main()
