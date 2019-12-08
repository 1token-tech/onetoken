const crypto=require('crypto')
const url=require('url')
function genNonce(){
    return Date.now()
}
function genSign({secret, verb, endpoint, nonce, dataStr}){
    if(!dataStr) dataStr=''
    let parsedUrl = url.parse(endpoint)
    path = parsedUrl.path
    message = verb.toUpperCase() + path + nonce + dataStr
    return getHash(secret,message)
} 
function getHash(secret,message){
    return crypto.createHmac('SHA256', secret).update(message).digest('hex')
}
module.exports={genSign,genNonce}