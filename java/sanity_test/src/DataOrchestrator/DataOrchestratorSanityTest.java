package DataOrchestrator;

import java.io.*;
import java.net.*;



public class DataOrchestratorSanityTest {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		String temp = "";
		String targetURL = "https://useraccount-stg.apixio.com:7076/auths";
		//String urlParameters = "";
	    //connection.setRequestProperty("email", "ishekhtman@apixio.com");
	    //connection.setRequestProperty("password", "apixio.123");
		
		
		String urlParameters = "";
		//try {
		//	urlParameters = "email=" + URLEncoder.encode("ishekhtman@apixio.com", "UTF-8") +"&password=" + URLEncoder.encode("apixio.123", "UTF-8");
		//} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
		//	e.printStackTrace();
		//}
		
		        
		        
		        
		temp = makeApiCall.excutePost(targetURL, urlParameters);
		System.out.println(temp);

	}

}
