package DataOrchestrator;

import java.io.*;
import java.net.*;
import java.security.Principal;
import java.util.*;
import java.io.IOException;
import java.io.PrintStream;
import java.net.InetAddress;



public class HttpURLConnectionExample2 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		
		//con.setRequestProperty("email", "ishekhtman@apixio.com");
		//con.setRequestProperty("password", "apixio.123");
		
			String addr = "https://useraccount-stg.apixio.com:7076/auths";
			String email = "ishekhtman@apixio.com";
			String password = "apixio.123";
			try{
			URL url = new URL(addr);
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			//String encoding = new sun.misc.BASE64Encoder().encode("emailpassword".getBytes());
			String encoding = new sun.misc.BASE64Encoder().encode("ishekhtman@apixio.com+apixio.123".getBytes());
			
			
			conn.setRequestProperty ("Authorization", "Basic " + encoding);
			conn.setRequestMethod("GET");

			conn.connect();
			InputStream in = conn.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(in));
			String text = reader.readLine();
			System.out.println(text);

			conn.disconnect();
			}catch(IOException ex)
			{
			ex.printStackTrace();
			System.out.println("made it here");
			}	

	}

}
