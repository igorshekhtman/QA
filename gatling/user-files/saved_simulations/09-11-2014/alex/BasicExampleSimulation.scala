package basic

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.http.Headers.Names._
import scala.concurrent.duration._
import bootstrap._
import assertions._

class BasicExampleSimulation extends Simulation {

  //val environment = "Production"
  //val environment = "Staging"
  
  var ip = "50.18.147.10"
  var userdatafn = "user_credentials_prod.csv"
  var patientdatafn = "patient_uuids_prod.csv"
  var documentdatafn = "document_uuids_prod.csv"
  
  val patientuuid = "7390113c-25dc-4203-99f9-55525027dce6"
  val documentuuid = "cac070a3-83fd-493c-86a4-2e2f5c57d56e"
  
  // Assigning vaiable values dependent on environment being Load Tested
  //if (environment == "Production") {
	//ip = "54.193.231.8"
	//userdatafn = "user_credentials_prod.csv"
	//patientdatafn = "patient_uuids_prod.csv"
	//documentdatafn = "document_uuids_prod.csv"
  //}
  //else {
	//ip = "50.18.147.10"
	//userdatafn = "user_credentials.csv"
	//patientdatafn = "patient_uuids.csv"
	//documentdatafn = "document_uuids.csv"  
  //} 
  
  // val login = ip + ":8085"
  // val login = ip + ":8076"
  // val token = ip + ":8085/tokens"
  
  val login = ip + ":8079"
  val loginSubmit = login + "/uh/login"
  val token = ip + ":8075/tokens"
  val document = ip + ":8085/document"
  val patient = ip + ":8085/patient"

  val thinkTime = 6 seconds
  val ok = 200
  val created = 201
  val accepted = 202
  val movedperm = 301
  val redirect = 302

  //val username = "root@api.apixio.com"
  //val password = "thePassword"
  
  //val username = "apxdemot0001@apixio.net"
  //val password = "Hadoop.4522"
  
  val scn = scenario("HCC app under load")
  
    .group("Login") {
      exec(
      http("Login page")
        .get(login)
        .check(status.is(ok)))

      .pause(thinkTime)
      .feed(csv(userdatafn))
      .exec(
        http("Submit login")
          .post(loginSubmit)
          .param("email", "${username}")

          .param("password", "${password}")

          .check(headerRegex("Set-Cookie","tomswebapps=(.*);").saveAs("externalToken"))
          .check(headerRegex("Set-Cookie","tomswebapps=(.*);").transform(value => {
              println("value = " + value.get)
              value}
          ))
          .check(status.is(redirect)))
        .pause(thinkTime)
    }
    .group("Token") {
      exec(
      http("Token exchange") // no think time
        .post(token)
        .header("Authorization", "Apixio ${externalToken}")
        .check(bodyString.transform(body => {
          println("body = " + body.get)
          body}
        ))
        .check(jsonPath("$.token").saveAs("internalToken"))
        .check(status.is(created)))
    }
    .group("Patient") {
      feed(csv(patientdatafn))
      .exec(
      //param ("patientuuid", "${patient_uuid}")  
      http("Patient demographics")
        //.param("patientuuid", "${username}")
        //.get(session => patient + "/" + patientuuid + "/demographics")
        .get("50.18.147.10:8085/patient/${patient_uuid}/demographics")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
        // TODO: Add other data checks here, i.e. Content-Type and response length
      .pause(thinkTime)
    }
    .group("Document") {
      feed(csv(documentdatafn))
      .exec( 
      http("Document retrieval text")
        .get("50.18.147.10:8085/document/${document_uuid}/text")
        //.get(session => document + "/" + documentuuid + "/text")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
      .exec( 
      http("Document retrieval metadata")
        .get("50.18.147.10:8085/document/${document_uuid}/metadata")
        //.get(session => document + "/" + documentuuid + "/metadata")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
      .exec( 
      http("Document retrieval file")
        .get("50.18.147.10:8085/document/${document_uuid}/file")
        //.get(session => document + "/" + documentuuid + "/file")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
        // TODO: Add other data checks here, i.e. Content-Type and response length
      .pause(thinkTime)
    }
    
  
  // 30 users over 20 min
  // setUp(scn.inject(ramp(30 users) over (1200 seconds)))
  // 30 users over 5 min
  // rampRate(5 usersPerSec) to(30 usersPerSec) during(60 seconds)
  // setUp(scn.inject(nothingFor(4 seconds), atOnce(10 users), ramp(10 users over 15 seconds), constantRate(30 usersPerSec) during (5 minutes)))
  // 
  // setUp(scn.inject(nothingFor(2 seconds), atOnce(2 users), ramp(11 users) over (5 minutes)))
// setUp(scn.inject(nothingFor(4 seconds), atOnce(30 users), ramp(60 users) over(60 minutes))) 
  
  // 
  // 
  // 
  // 60 users over 10 min
  // setUp(scn.inject(ramp(60 users) over (600 seconds)))
  // 30 users over 12 hours
  // setUp(scn.inject(ramp(30 users) over (43200 seconds)))
  // 60 users over 24 hours
  // setUp(scn.inject(ramp(60 users) over (86400 seconds)))
  // 30 users over 1 hour
  // setUp(scn.inject(ramp(30 users) over (3600 seconds)))
  // 3 users over 20 seconds
  setUp(scn.inject(ramp(3 users) over (20 seconds)))
  // 25 users over 120 seconds
  // setUp(scn.inject(ramp(25 users) over (120 seconds)))
  // 11 users over 1 hour
  // setUp(scn.inject(ramp(11 users) over (3600 seconds)))
  // 60 users over 1 hour
  // setUp(scn.inject(ramp(60 users) over (3600 seconds)))
    
  
    .protocols(http.baseURL("http://").disableFollowRedirect) // Note we can't use this because we use multiple services
    .assertions( // TODO: Fix, these are the assertions that came with the sample code
      global.successfulRequests.percent.is(100),
      details("Login" / "request_2").responseTime.max.lessThan(2000),
      details("request_9").requestsPerSec.greaterThan(10))
}
