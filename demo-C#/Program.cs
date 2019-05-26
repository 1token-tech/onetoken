using System;

namespace OneToken
{
    class Program
    {
        static void Main(string[] args)
        {
            var account = new Account("okef/liuzk2", "NO9A1zU8-JKsRHx1n-PwCXWCD8-3DxaBPtU", "1ZAcjRQr-Viw9DLiF-omc8dSPr-a0yqLAYf");
            Console.WriteLine("{0} {1} {2}", account.Symbol, account.TradeBaseUrl, account.WsBaseUrl);

            account.ConnectWs();
            
            var contract = "okef/eos.usd.q";

            Console.WriteLine(account.GetInfo());
            dynamic order = account.PlaceOrder(contract, 1, "b", 1);
            Console.WriteLine(order);
            if (order != null) {
                var oid = (string)order.exchange_oid;
                Console.WriteLine(account.GetOrderUseExchangeOid($"{oid}"));

                // cancel order use exchange oid
                Console.WriteLine(account.CancelUseExchangeOid(oid));

                Console.WriteLine(account.GetOrderUseExchangeOid($"{oid}"));
            }
            Console.WriteLine(account.GetOrderList(contract));
            while (true) {
                System.Threading.Tasks.Task.Delay(1000).Wait();
            }
            // var sign = account.GenerateSign("get", "/v1/trade/okef/mock/info", 1, "{\"exchange\": \"okef\"}");
            // Console.WriteLine(sign);
        }
    }
}
