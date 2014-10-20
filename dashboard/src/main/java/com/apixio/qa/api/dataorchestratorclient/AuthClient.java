package com.apixio.qa.api.dataorchestratorclient;

import org.apache.commons.io.IOUtils;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.impl.conn.PoolingClientConnectionManager;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;


public class AuthClient {
	private String username = "";
    private String password = "";
    private String authUrl =  "";
    private String tokenUrl = "";

    private String externalToken = "";
    private String internalToken = "";
    private boolean externallyAuthenticated = false;
    private boolean internallyAuthenticated = false;
    private DefaultHttpClient httpClient = null;

	public static void main (String[] args) throws Exception {

	}
	public AuthClient(String authUrl, String tokenUrl) {
        super();
		this.authUrl = authUrl;
		this.tokenUrl = tokenUrl;
	}
	public AuthClient(String username, String password, String authUrl, String tokenUrl) {
        super();
        // TODO: we are storing these in memory. Another plan grabs external token and discards these
        // Do we want this client to be able to reacquire a new External token? For now it will.
		this.username = username;
		this.password = password;
		this.authUrl = authUrl;
		this.tokenUrl = tokenUrl;
	}
   
    public String getAuthResponse(String email, String password, String code, Boolean internal, Integer ttl) throws Exception {
        ArrayList<BasicNameValuePair> formParams = new ArrayList<BasicNameValuePair>();
        formParams.add(new BasicNameValuePair("email", email));
        formParams.add(new BasicNameValuePair("password", password));
        formParams.add(new BasicNameValuePair("code", code));
        Map<String,Object> queryParams = new HashMap<String,Object>();
        queryParams.put("int", internal);
        queryParams.put("ttl", ttl);
        return getPostResult(authUrl, formParams, queryParams, false, true);
    }
    
    public String getInternalTokenResponse(String externalToken) throws IOException {
    	HttpPost httppost = new HttpPost(tokenUrl);
        httppost.addHeader("Authorization", "Apixio " + externalToken);
        HttpResponse response = executeRequest(httppost, false, true);
        return getResponseString(response);
    }

    protected String getAuthenticatedGetString(String url) throws Exception {
        HttpResponse response = getAuthenticatedGetResponse(url);
        return getResponseString(response);
    }

    protected byte[] getAuthenticatedGetBytes(String url) throws Exception {
        HttpResponse response = getAuthenticatedGetResponse(url);
        return EntityUtils.toByteArray(response.getEntity());
    }

    private DefaultHttpClient getThreadSafeClient() {
        if (httpClient == null) {
            HttpParams params = new BasicHttpParams();
            //params.setParameter(CoreConnectionPNames.CONNECTION_TIMEOUT, connectionTimeout);
            //params.setParameter(CoreConnectionPNames.SO_TIMEOUT, soTimeout);
            //params.setParameter(CoreProtocolPNames.USER_AGENT, buildUserAgent());

            PoolingClientConnectionManager connectionManager = new PoolingClientConnectionManager();
            //connectionManager.setMaxTotal(maxTotal);
            //connectionManager.setDefaultMaxPerRoute(defaultMaxPerRoute);

            httpClient = new DefaultHttpClient(connectionManager, params);
        }
        return httpClient;
    }

    private synchronized String getExternalToken() throws Exception {
        if (externallyAuthenticated) {
            return externalToken;
        } else {
            externalToken = getNewExternalToken();
            externallyAuthenticated = true;
            return externalToken;
        }
    }
    private synchronized String getInternalToken() throws Exception {
        if (internallyAuthenticated) {
            return internalToken;
        } else {
            internalToken = getNewInternalToken();
            internallyAuthenticated = true;
            return internalToken;
        }
    }

    private String getNewExternalToken() throws Exception {
    	String authResponse = getAuthResponse(username, password, null, null, null);
        JSONObject object = (JSONObject) JSONValue.parse(authResponse);
        String token = (String) object.get("token");
        System.out.println("Got External token: " + token);
        return token;
    }

    private String getNewInternalToken() throws Exception {
        JSONObject object = (JSONObject) JSONValue.parse(getPostResult(tokenUrl, null, null, true, true));
        String token = (String) object.get("token");
        System.out.println("Got Internal token: " + token);
        return token;
    }

    private HttpResponse getAuthenticatedGetResponse(String endpoint) throws Exception {
        HttpGet httpGet = new HttpGet(endpoint);
        return executeRequest(httpGet, true, false);
    }

    private String getPostResult(String endpoint, ArrayList<BasicNameValuePair> formParams, Map<String,Object> queryParams, boolean authenticated, boolean external) throws Exception {
    	String url = endpoint + getQueryString(queryParams);
    	HttpPost httppost = new HttpPost(url);
        if (authenticated && external)
            httppost.addHeader("Authorization", "Apixio " + getExternalToken());
        if (formParams != null)
            httppost.setEntity(new UrlEncodedFormEntity(formParams, "utf-8"));
        HttpResponse response = executeRequest(httppost, authenticated, external);
        return getResponseString(response);
    }

    private String getQueryString(Map<String, Object> queryParams) {
		String queryString = "";
    	if (queryParams != null && queryParams.size() > 0) {
			for (Entry<String, Object> queryParam : queryParams.entrySet()) {
				if (queryParam.getValue() != null) {
					if (queryString.equals("")) {
			    		queryString = "?";
					} else {
						queryString += "&";
					}
					queryString += queryParam.getKey() + "=" + queryParam.getValue();
				}
			}
    	}
		return queryString;
	}

	private String getResponseString(HttpResponse response) throws IOException {
        String responseString = null;
        if (response != null) {

            InputStreamReader isr = new InputStreamReader(response.getEntity().getContent());
            responseString = IOUtils.toString(isr);
        }
        return responseString;
    }

    private HttpResponse executeRequest(HttpUriRequest request, boolean authenticated, boolean external) {
        HttpResponse response = null;
        try {
            boolean retry = false;
            do {
                if (authenticated) {
                    if (external) {
                        request.setHeader("Authorization", "Apixio " + getExternalToken());
                    } else {
                        request.setHeader("Authorization", "Apixio " + getInternalToken());
                    }
                }
                retry = false;
                HttpClient httpClient = getThreadSafeClient();
                Long start = System.currentTimeMillis();
                response = httpClient.execute(request);
                long elapsedMillis = System.currentTimeMillis() - start;
                Integer statusCode = response.getStatusLine().getStatusCode();
                System.out.println("Execute request: " + request.getURI() + " - Status code: " +
                        response.getStatusLine().getStatusCode() + " (" + elapsedMillis + "ms)");
                if (statusCode == 200 || statusCode == 201) {
                    return response;
                } else if (statusCode == 401) {
                	if (authenticated) {
	                    if (external) {
	                        externallyAuthenticated = false;
	                    } else {
	                        internallyAuthenticated = false;
	                        retry = true;
	                    }
                	}
                } else if (statusCode == 403){
                    // ACL failure. Don't retry
                } else if (statusCode == 404){
                    // Not found. How to differentiate between API unavailable and data not found?
                    // Don't retry

                } else if (statusCode == 500) {
                    // do we want to keep alive while server throws 500? We may be causing it!
                }
                // TODO: What happens when server is just offline. I want stepped retry in that case. maybe.
            } while (retry);

        } catch (Exception e) {
            e.printStackTrace();
        }
        return response;
    }
}
