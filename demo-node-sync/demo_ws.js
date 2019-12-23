const WebSocket = require('ws');
const {genNonce,genSign}=require('./utils')
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  })
class AutoWS{
    constructor(url,headers,sendData,handler){
        this.url=url
        this.headers=headers
        this.sendData=sendData
        this.pingpongId=null
        this.socket=null
        this.pong=false
        this.handler=handler
        this.status=null
    }  
    connect(){
        if(this.pingpongId!==null){
            clearTimeout(this.pingpongId)
            this.pingpongId=null
        }
        if(this.status==='connecting'||this.status==='connected') return
        this.status='connecting'
        this.socket=new WebSocket(this.url,'',{headers:this.headers})
        this.socket.onopen=()=>{
            this.status='connected'
            this.sendData.forEach(msg=>{
                this.socket.send(msg)
            })
            this.pingpongCheck(this.socket)
        }
        this.socket.onmessage=(e)=>{
            let data=JSON.parse(e.data)
            if(data.uri==='pong') this.pong=true
            else this.handler&&this.handler(data)
        }
        this.socket.onclose=(e)=>{
            this.status='closed'
            try{this.socket.close()}catch(e){}
            this.connect()
        }
        this.socket.onerror=(e)=>{
            this.status='error'
            try{this.socket.close()}catch(e){}
            this.connect()
        }
    }
    pingpongCheck(socket){
        if(socket!==this.socket) return
        socket.send('{"uri":"ping"}')
        this.pong=false
        this.pingpongId=setTimeout(()=>{
            if(socket!==this.socket) return
            if(!this.pong){
                socket.close()
                this.connect()
            } else this.pingpongCheck(socket)
        },3000)
    }
}
class AccountWS{
    constructor({account,url,otSecret,otKey,sendData,handler}){
        this.account=account
        this.url=url
        let acctParts=account.split('/')
        let nonce = genNonce()
        let endpoint=`/ws/${acctParts[1]}`
        let sign = genSign({secret:otSecret, verb:'GET', endpoint, nonce})
        let headers = {'Api-Nonce': nonce.toString(), 'Api-Key': otKey, 'Api-Signature': sign,
                    'Content-Type': 'application/json'}
        this.ws=new AutoWS(url,headers,sendData,handler)
    }
    connect(){
        this.ws.connect()
    }
}
class InfoWS{
    constructor({account,otKey,otSecret,handler}){
        let url=`wss://1token.trade/api/v1/ws/trade/${account}`
        let sendData=['{"uri":"sub-info"}']
        this.ws=new AccountWS({account,url,otKey,otSecret,sendData,handler:msg=>{
            if(msg.uri==='info') handler&&handler(msg)
        }})
    }
    connect(){
        this.ws.connect()
    }
}
const secret={}
function demo(account){
    let infoWS=new InfoWS({account,otKey:secret.otKey,otSecret:secret.otSecret,handler:info=>{
        console.log('got info',info)
    }})
    infoWS.connect()
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
