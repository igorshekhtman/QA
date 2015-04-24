/**
 * Created by rezaalemy on 15-04-05.
 * This is a sample file created to show how we can intecept our services in protractor.
 * The technique is a little complicated, but it is possible.
 */

//The first step is, of course, to bring in the libraries that we need:

var LoginPage = require("../pages/login"), //the page for login.
    expect = require("chai").use(require("chai-as-promised")).expect,
    util = require("util"), //for a better console.log
    some_external_variable = "I am external variable", //to demonstrate passing variables
    _ = require("lodash"), //for better list and object manipulation.
    mock=require("../mock-helper");

describe("Basic Mocking with Protractor,", function () {

    // this is the outer shell of our test suite. we set up and tear down here.

    before(function () {
        this.timeout(10000); //may take a while to login
        var login = new LoginPage();
        return login.validLogin().then(function () {
            expect(login.assert_logged_in()).to.eventually.eq(true);
        });
    });

    //Ok now we have logged in, we can begin our tests.

    describe("Simple Mocking of a Service: ", function () {
        var lastLogs = []; //this to save the logs in the afterEach function.

        it("Should first get the service, using execute Async Script", function () {

            var spyOnProject=function(callerargs,myargs){ //spy function should be self contained!
                console.info("Spying on Project got ",
                    callerargs,
                    myargs[0],
                    "passing through");

                return this.mockedProperties.getProject.apply(this,callerargs);
            }.toString();

            mock.mockServiceFunction("modelServer",
                "getProject",
                spyOnProject,
                some_external_variable)
                .then(function(data){
                    expect(data).to.contain("Success");
                });
        });
        it("should now wait for more than a minute, so that the mocked service will be called", function () {
            this.timeout(1000000); //so that mocha won't time out!
            browser.sleep(70000); //we sleep (or do something that would call our mocked function),
            mock.flushBrowserLogs();
        });
        it("should now have access to the browser logs, to see what happened while he was sleep", function () {
            var mockActiveLog=mock.findInfoLog(lastLogs,function(params){
                if(params.length===4)
                    if(params[0].value.indexOf("Spying on Project got ")>-1)
                        if(params[1].subtype="array")
                            if(params[2].value.indexOf("I am external variable")>-1)
                                if(params[3].value === "passing through")
                                    return true;
                return false;
            });
            expect(mockActiveLog).to.be.ok;
        });
        afterEach(function () {
            // this is a nice technique to make sure we didn't get an error during our tests.
            mock.getBrowserLogs().then(function (logs) {
                lastLogs = logs;
                var errorLog = mock.findErrorLog(logs);
                console.log("\n", "Log: ", util.inspect(logs) + "\n=========>end of log\n");
//                expect(errorLog).to.not.be.ok; //uncomment this and we will catch the errors.
            });
        });
        after(function(){
            mock.clearMock("modelServer","getProject").then(function(result){
                expect(result).to.contain("Success");
            });
        });
    });
});
