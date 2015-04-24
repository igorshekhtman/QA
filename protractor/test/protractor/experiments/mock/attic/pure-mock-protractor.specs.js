/**
 * Created by rezaalemy on 15-04-05.
 * This is a sample file created to show how we can intecept our services in protractor.
 * The technique is a little complicated, but it is possible.
 */

//The first step is, of course, to bring in the libraries that we need:

var LoginPage = require("../../../pages/login"), //the page for login.
    expect = require("chai").use(require("chai-as-promised")).expect,
    util = require("util"), //for a better console.log
    some_external_variable = "I am external variable", //to demonstrate passing variables
    _ = require("lodash"); //for better list and object manipulation.

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
            browser.executeAsyncScript(function (arrayOfStrings, externalVariable, callback) {
                //inside this function, there is no closure. we can't see
                //anything outside, unless we have passed it

                //now to get our angular components, we need its injector.
                //of course all three lines below could be collapsed into one,
                //but for clarity let's leave them apart. if there is a controller on the page, there is
                //something with class of ng-scope.

                var injector = angular.element(document.querySelector(".ng-scope")).injector();
                //and from that we can get services:
                var modelServer = injector.get("modelServer");
                // now let's mock one of it's functions:
                var getProject = modelServer.getProject;

                // fine. mock it.
                modelServer.getProject = function () {
                    //note that console.log won't work, and best results are with info.
                    console.info("mock in effect! I was called with ", arguments);
                    return getProject.apply(modelServer, arguments);
                };

                // and get something back to our protractor instance. this is just for show.
                var s = "";
                for (var i in modelServer) s += i + ", ";
                console.info("Mocked the project", arrayOfStrings[0], externalVariable);
                callback("Mocked getProject. model server had the following keys: " + s);

            }, ["Sample Data to be passed", "can come from a closure"], some_external_variable)
                .then(function (result) {
                    //this block is entered when the callback is called. we will get a single variable
                    //containing the first argument passed to callback.
                    console.log(result);
                    expect(result).to.contain("Mocked getProject.");
                    //the current logs of the project are available after this test.
                })
        });
        it("should now see the logs that were generated during the previous test.", function () {
            var mockStartLog = _.find(lastLogs, function (log) {
                if (log.level.name !== "WARNING")
                    return false;
                var params = JSON.parse(log.message).message.parameters;
                if (params.length === 3)
                    if (params[0].value.indexOf("Mocked the project") > -1)
                        if (params[1].value.indexOf("Sample Data to be passed") > -1)
                            if (params[2].value.indexOf("I am external variable") > -1)
                                return true;
                return false;
            });
            expect(mockStartLog).to.be.ok;
        });
        it("should now wait for more than a minute, so that the mocked service will be called", function () {
            this.timeout(1000000); //so that mocha won't time out!
            browser.sleep(70000); //we sleep (or do something that would call our mocked function),
            browser.executeAsyncScript(function (callback) { //then we flush the logs;
                callback();
            });
        });
        it("should now have access to the browser logs, to see what happened while he was sleep", function () {
            var mockActiveLog = _.find(lastLogs, function (log) {
                if (log.level.name === "WARNING")
                    return _.find(JSON.parse(log.message).message.parameters, function (parameter) {
                        return parameter.value.indexOf("mock in effect! I was called") > -1;
                    });
                return false;
            });
            expect(mockActiveLog).to.be.ok;
        });
        afterEach(function () {
            // this is a nice technique to make sure we didn't get an error during our tests.
            browser.manage().logs().get('browser').then(function (logs) {
                lastLogs = logs;
                var errorLog = _.find(logs, function (log) {
                    return log.level.name === "SEVERE";
                });
                //comment this to be a little less verbose.
                console.log("\n", "Log: ", util.inspect(logs) + "\n=========>end of log\n");
//                expect(errorLog).to.not.be.ok; //uncomment this and we will catch the errors.
            });
        });
    });
});
