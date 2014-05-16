package basic

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.http.Headers.Names._
import scala.concurrent.duration._
import bootstrap._
import assertions._

class BasicExampleSimulation extends Simulation {

  var patientuuid = "4e74c4a1-9af5-477f-a05a-e32e62c690aa"
  var documentuuid = "9d9a36cd-28c3-4c05-a0c1-748de6b0d94e"
  
  val login = "54.193.204.86:8079"
  val loginSubmit = login + "/uh/login"
  val token = "54.193.204.86:8075/tokens"
  val document = "54.193.204.86:8085/document"
  val patient = "54.193.204.86:8085/patient"

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
      .feed(csv("user_credentials.csv"))
      .exec(
        http("Submit login")
          .post(loginSubmit)
          .param("email", "${username}")
          .param("password", "${password}")
          .check(headerRegex("Set-Cookie","tomswebapps=(.*);").saveAs("externalToken"))
          //.check(headerRegex("Set-Cookie","tomswebapps=(.*);").transform(value => {
          //  println("value = " + value.get)
          //  value}
          //))
          .check(status.is(redirect)))
        .pause(thinkTime)
    }
    .group("Token") {
      exec(
      http("Token exchange") // no think time
        .post(token)
        .header("Authorization", "Apixio ${externalToken}")
        //.check(bodyString.transform(body => {
        //  println("body = " + body.get)
        //  body}
        //))
        .check(jsonPath("$.token").saveAs("internalToken"))
        .check(status.is(created)))
    }
    .group("Patient") {
      feed(csv("patient_uuids.csv"))
      .exec(
      //param ("patientuuid", "${patient_uuid}")  
      http("Patient demographics")
        //.param("patientuuid", "${username}")
        //.get(session => patient + "/4e74c4a1-9af5-477f-a05a-e32e62c690aa" + "/demographics")
        .get("54.193.204.86:8085/patient/${patient_uuid}/demographics")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
        // TODO: Add other data checks here, i.e. Content-Type and response length
      .pause(thinkTime)
    }
    .group("Document") {
      feed(csv("document_uuids.csv"))
      .exec( 
      http("Document retrieval text")
        .get("54.193.204.86:8085/document/${document_uuid}/text")
        //f6bc5be1-fe39-4146-89d5-f3eb724d6591 - bad document
        //2c10e935-ffe9-441e-a0b6-cf7aaa768063
        //.get("54.193.204.86:8085/document/2c10e935-ffe9-441e-a0b6-cf7aaa768063/text")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
      .exec( 
      http("Document retrieval metadata")
        .get("54.193.204.86:8085/document/${document_uuid}/metadata")
        //.get("54.193.204.86:8085/document/2c10e935-ffe9-441e-a0b6-cf7aaa768063/metadata")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
      .exec( 
      http("Document retrieval file")
        .get("54.193.204.86:8085/document/${document_uuid}/file")
        //.get("54.193.204.86:8085/document/2c10e935-ffe9-441e-a0b6-cf7aaa768063/file")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
        // TODO: Add other data checks here, i.e. Content-Type and response length
      .pause(thinkTime)
    }
    
  
  // 30 users over 20 min
  // setUp(scn.inject(ramp(30 users) over (1200 seconds)))
  // 60 users over 10 min
  setUp(scn.inject(ramp(60 users) over (600 seconds)))
  // 30 users over 12 hours
  //setUp(scn.inject(ramp(30 users) over (43200 seconds)))
  // 3 users over 20 seconds
  //setUp(scn.inject(ramp(3 users) over (20 seconds)))
  
    .protocols(http.baseURL("http://").disableFollowRedirect) // Note we can't use this because we use multiple services
    .assertions( // TODO: Fix, these are the assertions that came with the sample code
      global.successfulRequests.percent.is(100),
      details("Login" / "request_2").responseTime.max.lessThan(2000),
      details("request_9").requestsPerSec.greaterThan(10))
}
