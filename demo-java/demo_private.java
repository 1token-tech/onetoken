import okhttp3.*;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class demo_private {

    public static String ot_key = "";
    public static String ot_secret = "";
    public String HOST = "https://1token.trade/api/v1/trade";
    public int TimeOut = 15000;
    public OkHttpClient client;


    public demo_private() {

    }

    public static void main(String[] args) throws IOException, JSONException {
        Scanner sc = new Scanner(System.in);

        System.out.println("ot_key:");
        ot_key = sc.next();

        System.out.println("ot_secret:");
        ot_secret = sc.next();

        System.out.println("请输入交易账号 账号格式是 {交易所}/{交易账户名} 比如 okex/mock-1token-demo: ");

        String account = sc.next();

        demo_private d = new demo_private();
        d.demo(account);
    }

    public String sha256_HMAC(String secret, String message) {
        String hash = "";
        try {
            Mac sha256_HMAC = Mac.getInstance("HmacSHA256");
            SecretKeySpec secret_key = new SecretKeySpec(secret.getBytes(), "HmacSHA256");
            sha256_HMAC.init(secret_key);
            byte[] bytes = sha256_HMAC.doFinal(message.getBytes());
            hash = byteArrayToHexString(bytes);
            System.out.println(hash);
        } catch (Exception e) {
            System.out.println("Error HmacSHA256 ===========" + e.getMessage());
        }
        return hash;
    }

    private String byteArrayToHexString(byte[] b) {
        StringBuilder hs = new StringBuilder();
        String stmp;
        for (int n = 0; b != null && n < b.length; n++) {
            stmp = Integer.toHexString(b[n] & 0XFF);
            if (stmp.length() == 1)
                hs.append('0');
            hs.append(stmp);
        }
        return hs.toString().toLowerCase();
    }

    public String gen_nonce() {
        return String.valueOf(System.currentTimeMillis() / 1000);
    }

    //获取签名
    public String gen_sign(String secret, String verb, String endpoint, String nonce, String data_str) {


        if (data_str == null) {
            data_str = "";
        }

        String message = verb + endpoint + nonce + data_str;

        String signature = sha256_HMAC(secret, message);

        return signature;
    }

    //TimeOut给0 就是使用默认值  HOST也是传""或者null就是使用默认值
    public Response api_call(String method, String endpoint, HashMap<String, String> params, String jsonData, int timeOut, String host) throws IOException {

        if (timeOut == 0) {
            timeOut = TimeOut;
        }

        if (host == null || host.equals("")) {
            host = HOST;
        }

        //请求方式大写
        method = method.toUpperCase();

        String nonce = gen_nonce();

        String url = host + endpoint;

        String sign = gen_sign(ot_secret, method, endpoint, nonce, jsonData);

        String params_str = "";

        if (params != null) {
            for (Map.Entry<String, String> entry : params.entrySet()) {
                params_str += "&" + entry.getKey() + "=" + entry.getValue();
            }
            params_str = "?" + params_str.substring(1, params_str.length() - 1);
        }

        url = url + params_str;


        MediaType mediaType = MediaType.parse("application/json");
        RequestBody requestBody = RequestBody.create(mediaType, jsonData);

        Request request = new Request.Builder().url(url).method(method, method.equals("GET") ? null : requestBody).
                addHeader("Api-Nonce", nonce).
                addHeader("Api-Key", ot_key).
                addHeader("Api-Signature", sign).
                addHeader("Content-Type", "application/json").
                build();

        Response response = client.newCall(request).execute();

        return response;
    }

    public void demo(String account) throws IOException, JSONException {

        client = new OkHttpClient();

        System.out.println("查看账户信息");
        Response r = api_call("GET", "/" + account + "/info", null, "", 0, "");
        System.out.println(r.body() != null ? r.body().string() : "");


        System.out.println("撤销所有订单");
        r = api_call("DELETE", "/" + account + "/orders/all", null, "", 0, "");
        System.out.println(r.body() != null ? r.body().string() : "");

        System.out.println("下单");

        JSONObject jsonObjectParams = new JSONObject();
        jsonObjectParams.put("contract", "okex/btc.usdt");
        jsonObjectParams.put("price", 10);
        jsonObjectParams.put("bs", "b");
        jsonObjectParams.put("amount", 1);
        JSONObject jsonObjectParams_1 = new JSONObject();
        jsonObjectParams_1.put("close", true);
        jsonObjectParams.put("options", jsonObjectParams_1);

        r = api_call("POST", "/" + account + "/orders", null, jsonObjectParams.toString(), 0, "");
        String result = r.body().string();
        System.out.println(result);

        JSONObject jsonObject = new JSONObject(result);
        String exchange_oid = jsonObject.getString("exchange_oid");


        System.out.println("查询挂单 应该有一个挂单");
        //这边解析用的原生的jsonObject 可自行选择适合的库
        r = api_call("GET", "/" + account + "/orders", null, "", 0, "");
        JSONArray jsonArray = new JSONArray(r.body().string());
        System.out.println(jsonArray.length());


        System.out.println("用 exchange_oid撤单");
        HashMap<String, String> params = new HashMap<>();
        params.put("exchange_oid", exchange_oid);
        r = api_call("DELETE", "/" + account + "/orders", params, "", 0, "");
        System.out.println(r.body() != null ? r.body().string() : "");


        System.out.println("查询挂单 应该没有挂单");
        r = api_call("GET", "/" + account + "/orders", null, "", 0, "");
        JSONArray jsonArray_1 = new JSONArray(r.body().string());
        System.out.println(jsonArray_1.length());

    }

}
