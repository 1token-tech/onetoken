using System;
using System.Text;
using System.IO;
using System.Security.Cryptography;
using System.Net;
using System.Net.Http;
using Newtonsoft.Json;
using System.Net.Http.Headers;
using System.Collections.Generic;
using System.Web;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;
using System.Linq;

namespace OneToken {

    public class Account {
        
        public string Symbol {get;set;}
        
        private string OtKey {get; set;}

        private string OtSecret {get; set;}

        public string Name {get; private set;}

        public string Exchange {get; private set;}

        public string TradeBaseUrl {
            get {
                return $"{Constants.TradeHost}/{this.Symbol}";
            }
        }
        
        public string WsBaseUrl {
            get {
                return $"{Constants.TradeWsHost}/{this.Symbol}?source=csharp";
            }
        }

        private HttpClient HttpClient; 

        private ClientWebSocket WsClient;

        public Account(string symbol, string otKey=null, string otSecret=null) {
            this.Symbol = symbol;
            if (otKey != null) {
                this.OtKey = otKey;
                this.OtSecret = otSecret;
            } else {
                string homePath = (Environment.OSVersion.Platform == PlatformID.Unix || 
                   Environment.OSVersion.Platform == PlatformID.MacOSX)
                    ? Environment.GetEnvironmentVariable("HOME")
                    : Environment.ExpandEnvironmentVariables("%HOMEDRIVE%%HOMEPATH%");
                string configPath = $"{homePath}\\.onetoken\\config.yml";
                if (System.IO.File.Exists(configPath)) {
                    var reader = new StreamReader(configPath);
                    while (!reader.EndOfStream) {
                        var line = reader.ReadLine();
                        var elements = line.Split(":");
                        switch(elements[0]) {
                            case "ot_key":
                            case "api_key":
                                this.OtKey = elements[1].Trim();
                                break;
                            case "ot_secret":
                            case "api_secret":
                                this.OtSecret = elements[1].Trim();
                                break;
                        }
                    }
                    reader.Close();
                } else {
                    throw new Exception($"please setup your onetoken config file {configPath}");
                }
            }
            var eles = symbol.Split('/');
            this.Exchange = eles[0];
            this.Name = eles[1];
            this.HttpClient = new HttpClient();
            this.HttpClient.BaseAddress = new Uri(this.TradeBaseUrl);
            this.HttpClient.DefaultRequestHeaders.Accept.Clear();
            this.HttpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            this.WsClient = new ClientWebSocket();
        }

        public string GenerateSign(string method, string endpoint, string nonce, string data_json) {
            if (data_json == null) {
                data_json ="";
            }
            method = method.ToUpper();
            var message = method + endpoint + nonce + data_json;
            var messageData = Encoding.UTF8.GetBytes(message);
            var secret = Encoding.UTF8.GetBytes(this.OtSecret);
            var mac = new HMACSHA256(secret);
            var hash = mac.ComputeHash(messageData);
            var signature = BitConverter.ToString(hash).Replace("-", "").ToLower();
            return signature;
        }

        public object ApiCall(string method, string endpoint, IDictionary<string, object> param=null, IDictionary<string, object> data=null, float timeout=15) {
            method = method.ToUpper();
            var httpMethod = HttpMethod.Get;
            switch (method) {
                case "POST":
                    httpMethod = HttpMethod.Post;
                    break;
                case "DELETE":
                    httpMethod = HttpMethod.Delete;
                    break;
                case "PATCH":
                    httpMethod = HttpMethod.Patch;
                    break;
            }
            var url = TradeBaseUrl + endpoint;
            if (param != null) {
                url += "?";
                foreach(var kv in param) {
                    if (kv.Value == null){
                        continue;
                    }
                    var key = HttpUtility.UrlEncode(kv.Key);
                    var value = HttpUtility.UrlEncode(kv.Value.ToString());
                    url += $"{key}={value}";
                }
            }
            using (var request = new HttpRequestMessage(httpMethod, url))
            {
                var data_json = "";
                if (data != null){
                    data_json = JsonConvert.SerializeObject(data, Formatting.None, new JsonSerializerSettings{NullValueHandling=NullValueHandling.Ignore});
                    var stringContent = new StringContent(data_json, Encoding.UTF8, "application/json");
                    request.Content = stringContent;
                }   
                var nonce = DateTime.Now.Ticks.ToString();
                var uri = $"/{Exchange}/{Name}{endpoint}";
                var sign = GenerateSign(method, uri, nonce, data_json);
                request.Headers.Add("Api-Nonce", nonce);
                request.Headers.Add("Api-Key", OtKey);
                request.Headers.Add("Api-Signature", sign);
                using (var response = this.HttpClient
                    .SendAsync(request, HttpCompletionOption.ResponseHeadersRead).Result)
                {
                    if (!response.IsSuccessStatusCode) {
                        return null;
                    }
                    var txt = response.Content.ReadAsStringAsync().Result;
                    return JsonConvert.DeserializeObject(txt);
                }
            }
        }

        public object GetInfo() {
            return ApiCall("get", "/info");
        }

        public object GetOrderList(string contract, string state=null, string source=null) {
            var param = new Dictionary<string, object>(){
                {"contract", contract},
                {"state", state},
                {"helper", source}
            };
            return ApiCall("get", "/orders", param);
        }

        public object PlaceOrder(string contract, double price, string bs, double amount, string clientOid=null, IDictionary<string, object> tags=null, IDictionary<string, object> options=null) {
            var data = new Dictionary<string, object>() {
                {"contract", contract},
                {"price", price},
                {"bs", bs},
                {"amount", amount},
                {"client_oid", clientOid},
                {"tags", tags},
                {"options", options},
            };
            return ApiCall("post", "/orders", null, data);
        }

        public object CancelUseExchangeOid(string exchangeOid) {
            var param = new Dictionary<string, object>() {
                {"exchange_oid", exchangeOid}
            };
            return ApiCall("delete", "/orders", param);
        }

        public object GetOrderUseExchangeOid(string oids) {
            var param = new Dictionary<string, object>() {
                {"exchange_oid", oids}
            };
            return ApiCall("get", "/orders", param);
        }

        public async void ConnectWs() {
            var uri = new Uri(WsBaseUrl);
            var nonce = DateTime.Now.Ticks.ToString();
            var sign = GenerateSign("GET", $"/ws/{Name}", nonce, null);
            WsClient.Options.SetRequestHeader("Api-Nonce", nonce);
            WsClient.Options.SetRequestHeader("Api-Key", OtKey);
            WsClient.Options.SetRequestHeader("Api-Signature", sign);
            await this.WsClient.ConnectAsync(uri, CancellationToken.None);

            Console.WriteLine($"Connected to ws {WsClient.State}");
            var task = new Task(() => OnWsMessages());
            task.Start();
            new Task(() => HeartBeat()).Start();
            var subInfo = JsonConvert.SerializeObject(new {uri="sub-info"});
            var subOrder = JsonConvert.SerializeObject(new {uri="sub-order"});
            SendString(subInfo);
            SendString(subOrder);
        }

        public async void SendString(string json) {
            // Console.WriteLine($"send text to ws {json}");
            await this.WsClient.SendAsync(new ArraySegment<byte>(Encoding.ASCII.GetBytes(json)),
                WebSocketMessageType.Text, true, CancellationToken.None);
        }

        public async void HeartBeat() {
            while (this.WsClient.State == WebSocketState.Open) {
                SendString(JsonConvert.SerializeObject(new {uri="ping"}));
                SendString(JsonConvert.SerializeObject(new {uri="papap"}));
                await Task.Delay(5000);
            }
        }

        private async void OnWsMessages() {
            while(this.WsClient.State == WebSocketState.Open) {
                byte[] buffer = new byte[65536];
                var segment = new ArraySegment<byte>(buffer, 0, buffer.Length);
                var recvResult = await WsClient.ReceiveAsync(segment, CancellationToken.None);
                switch(recvResult.MessageType) {
                    case WebSocketMessageType.Text:
                        var msg = Encoding.UTF8.GetString(segment.Array.Take(recvResult.Count).ToArray());
                        var item = (dynamic)JsonConvert.DeserializeObject(msg);
                        var uri = item.uri.ToString();
                        switch(uri) {
                            case "ping":
                            case "pong":
                            case "status":
                                break;
                            case "info":
                                Console.WriteLine("info updated");
                                break;
                            case "order":
                                Console.WriteLine("order updated");
                                break;
                            default:
                                Console.WriteLine($"unknown uri {uri}");
                                break;
                        }

                        break;
                    default:
                        Console.WriteLine(recvResult.MessageType);
                        break;
                }
            }
            Console.WriteLine($"websocket is closed. {WsClient.State}");
            ConnectWs();
        }

    }
}