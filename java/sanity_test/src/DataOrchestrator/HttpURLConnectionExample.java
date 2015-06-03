package DataOrchestrator;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
 
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLPeerUnverifiedException;


public class HttpURLConnectionExample {
	
	private final String USER_AGENT = "Mozilla/5.0";
	 
	public static void main(String[] args) throws Exception {
 
		HttpURLConnectionExample http = new HttpURLConnectionExample();

 
		System.out.println("Testing 1 - Send Http GET request");
		http.sendGet();
		//new HttpsClient().sendGet();
 
		System.out.println("\nTesting 2 - Send Http POST request");
		http.sendPost();
 
	}
 
	// HTTP GET request
	private void sendGet() throws Exception {
 
		//String url = "https://useraccount-stg.apixio.com:7076/auths";
		//URL obj = new URL(url);
		//HttpURLConnection con = (HttpURLConnection) obj.openConnection();
		
		String https_url = "https://useraccount-stg.apixio.com:7076/auths";
	    URL url;
	    url = new URL(https_url);
	    HttpsURLConnection con = (HttpsURLConnection)url.openConnection();
		
		
		
		
		
		//HttpsURLConnection cons = (HttpsURLConnection) obj.openConnection()
		//conns = javax.net.ssl.HttpsURLConnection;
 
		// optional default is GET
		con.setRequestMethod("GET");
 
		//add request header
		con.setRequestProperty("User-Agent", USER_AGENT);
		con.setRequestProperty("Content-Type", "application/json");

	    //connection.setRequestProperty("Content-Length", Integer.toString(urlParameters.getBytes().length));
		con.setRequestProperty("Referer", "https://useraccount-stg.apixio.com:7076");
	    
		con.setRequestProperty("Content-Length", "48");
	    
		con.setRequestProperty("Content-Language", "en-US");  
	    
		con.setRequestProperty("email", "apxdemot01@apixio.net");
		con.setRequestProperty("password", "Hadoop.4522");
		
		
		
		
		//String urlParameters = "email=ishekhtman@apixio.com&password=apixio.123";
		
		
 
		//int responseCode = con.getResponseCode();
		// Send post request
		//con.setDoOutput(true);
		//DataOutputStream wr = new DataOutputStream(con.getOutputStream());
		//wr.writeBytes(urlParameters);
		//wr.flush();
		//wr.close();
		
		
		
		int responseCode = con.getResponseCode();
		System.out.println("\nSending 'GET' request to URL : " + url);
		System.out.println("Response Code : " + responseCode);
 
		BufferedReader in = new BufferedReader(
		        new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();
 
		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();
 
		//print result
		System.out.println(response.toString());
 
	}
 
	// HTTP POST request
	private void sendPost() throws Exception {
 
		String url = "https://selfsolve.apple.com/wcResults.do";
		URL obj = new URL(url);
		HttpsURLConnection con = (HttpsURLConnection) obj.openConnection();
 
		//add request header
		con.setRequestMethod("POST");
		con.setRequestProperty("User-Agent", USER_AGENT);
		con.setRequestProperty("Accept-Language", "en-US,en;q=0.5");
 
		String urlParameters = "sn=C02G8416DRJM&cn=&locale=&caller=&num=12345";
 
		// Send post request
		con.setDoOutput(true);
		DataOutputStream wr = new DataOutputStream(con.getOutputStream());
		wr.writeBytes(urlParameters);
		wr.flush();
		wr.close();
 
		int responseCode = con.getResponseCode();
		System.out.println("\nSending 'POST' request to URL : " + url);
		System.out.println("Post parameters : " + urlParameters);
		System.out.println("Response Code : " + responseCode);
 
		BufferedReader in = new BufferedReader(
		        new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();
 
		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();
 
		//print result
		System.out.println(response.toString());
 
	}
 
	

}
