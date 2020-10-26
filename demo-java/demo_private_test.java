import org.json.JSONException;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class demo_private_test {


    public static void main(String[] args) throws IOException, JSONException {
        String home = System.getProperty("user.home");
        System.out.println(home);
        BufferedReader reader = new BufferedReader(new FileReader(home + "/.onetoken/config.yml"));

        String line1 = reader.readLine();
        String line2 = reader.readLine();
        demo_private.ot_key = line1.split(":")[1].trim();
        demo_private.ot_secret = line2.split(":")[1].trim();


        String account = "okex/mock-1token-demo";
        demo_private d = new demo_private();
        d.demo(account);
    }

}
