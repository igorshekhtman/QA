
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class DataOrchestratorSimulation extends Simulation {

  //===================== Global Test Environment Selection ========================
  //val environment = "Production"
  val environment = "Staging"

  val numberofusers = 1
  val testduration = 10 seconds
  //================================================================================

  //===== Variable declaration, initialization =============
  var userdatafn = "user_credentials-prd.csv"
  var patientdatafn = "patient_uuids-prd.csv"
  var documentdatafn = "document_uuids-prd.csv"
  var useraccount = "useraccount-prd.apixio.com"
  var tokenizer = "tokenizer-prd.apixio.com"
  var dataorchestrator = "dataorchestrator-prd.apixio.com"
  var postfix = "-prd"

  if (environment == "Production") {
    postfix = "-prd"
  }
  else {
    postfix = "-stg"
  }

  userdatafn = "user_credentials" + postfix + ".csv"
  patientdatafn = "patient_uuids" + postfix + ".csv"
  documentdatafn = "document_uuids" + postfix + ".csv"
  useraccount = "useraccount" + postfix + ".apixio.com"
  tokenizer = "tokenizer" + postfix + ".apixio.com"
  dataorchestrator = "dataorchestrator" + postfix + ".apixio.com"

  val auth = useraccount + ":7076/auths"
  val token = tokenizer + ":7075/tokens"
  val document = dataorchestrator + ":7085/document"
  val patient = dataorchestrator + ":7085/patient"
  val event = dataorchestrator + ":7085/events"
  val util = dataorchestrator + ":7085/util"

  val thinkTime = 6 seconds
  val ok = 200
  val created = 201
  val accepted = 202
  val movedperm = 301
  val redirect = 302

  //val username = "root@api.apixio.com"
  //val password = "thePassword"

  println("Environment: "+environment+" --> "+useraccount)

  val scn = scenario("Data Orch API load test")


    .group("Authorization") {
    feed(csv(userdatafn))
      .exec(
        http("Submit authorization")
          .post(auth)
          .formParam("email", "${username}")
          .formParam("password", "${password}")
          .check(jsonPath("$.token").saveAs("externalToken"))
          .check(jsonPath("$.token").transform { value: String => {
          println("value = " + value.get)
          value
        }})
          .check(status.is(ok)))
      .pause(thinkTime)
  }


    .group("Token") {
    exec(
      http("Token exchange") // no think time
        .post(token)
        .header("Authorization", "Apixio ${externalToken}")
        .check(bodyString.transform { body: String => {
        println("body = " + body.get)
        body
      }})
        .check(jsonPath("$.token").saveAs("internalToken"))
        .check(jsonPath("$.token").transform { value: String => {
          println("value = " + value.get)
          value
        }})
        .check(status.is(created)))
  }
    .group("Patient") {
    feed(csv(patientdatafn))
      .exec(
        http("Patient demographics")
          .get(patient+"/${patient_uuid}/demographics")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform { (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))

      .exec(
        http("Patient apo")
          .get(patient+"/${patient_uuid}/apo")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform { (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))
      .pause(thinkTime)
  }

   // .group("Event") {
   // feed(csv(patientdatafn))
   // .exec(
   //   http("Events")
   //     .get(event)
   //     .header("Authorization", "Apixio ${internalToken}")
   //     .check(status.is(ok)))
   //   .pause(thinkTime)
  //}

    .group("Util") {
    exec(
      http("Util healthcheck")
        .get(util+"/healthcheck")
        .header("Authorization", "Apixio ${internalToken}")
        .check(status.is(ok)))
      .pause(thinkTime)

     // .exec(
     //   http("Util refreshBeans")
     //     .get(util+"/refreshBeans")
     //     .header("Authorization", "Apixio ${internalToken}")
     //     .check(status.is(ok)))
     // .pause(thinkTime)

    .exec(
    http("Util version")
         .get(util+"/version")
         .header("Authorization", "Apixio ${internalToken}")
         .check(status.is(ok)))
       .pause(thinkTime)

    //.exec(
    //http("Util config")
    //     .get(util+"/config")
    //     .header("Authorization", "Apixio ${internalToken}")
    //     .check(status.is(ok)))
    //  .pause(thinkTime)
    }

    .group("Document") {
    feed(csv(documentdatafn))
      .exec(
        http("Document text")
          .get(document+"/${document_uuid}/text")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))

      .exec(
        http("Document metadata")
          .get(document+"/${document_uuid}/metadata")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))

      .exec(
        http("Document file")
          .get(document+"/${document_uuid}/file")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))

      .exec(
        http("Document textcontent")
          .get(document+"/${document_uuid}/textContent")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))

      .exec(
        http("Document simplecontent")
          .get(document+"/${document_uuid}/simpleContent")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))


      .exec(
        http("Document rawcontent")
          .get(document+"/${document_uuid}/rawContent")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))


      .exec(
        http("Document extractedcontent")
          .get(document+"/${document_uuid}/extractedContent")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))


      .exec(
        http("Document apo")
          .get(document+"/${document_uuid}/apo")
          .header("Authorization", "Apixio ${internalToken}")
          .check(status.is(ok))
          .check(status.transform{ (status: Int, session: Session) =>
          println("status : " + status)
          println("date : " + new java.util.Date)
          println(session.attributes)
          null
        }))

      .pause(thinkTime)
  }

  // setUp(scn.inject(ramp(30 users) over (1200 seconds)))
  // rampRate(5 usersPerSec) to(30 usersPerSec) during(60 seconds)
  // setUp(scn.inject(nothingFor(4 seconds), atOnce(10 users), ramp(10 users over 15 seconds), constantRate(30 usersPerSec) during (5 minutes)))
  // setUp(scn.inject(nothingFor(2 seconds), atOnce(2 users), ramp(11 users) over (5 minutes)))
  // setUp(scn.inject(nothingFor(4 seconds), atOnce(30 users), ramp(60 users) over(60 minutes)))
  //
  setUp(scn.inject(rampUsers(numberofusers) over (testduration)))


    .protocols(http.baseURL("https://").disableFollowRedirect) // Note we can't use this because we use multiple services
    .assertions(
      global.successfulRequests.percent.is(100))
}
