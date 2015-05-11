/**
 * Created by rezaalemy on 15-04-02.
 */

var backendProxy = require('http-backend-proxy'),
    mockData = require('./mockModel'),
    LoginPage = require("../pages/login"),
    expect   = require('chai').use(require('chai-as-promised')).expect,
    util=require('util'),
    _=require('lodash');



describe("basic http proxy testing", function () {
    before(function () {
        this.timeout(20000);
        var login = new LoginPage(https_address);
        return login.getPage().then(function () {
            return login.login(valid_user, valid_pass).then(function () {
                console.log("\n====>Should have logged in now\n");
            });
        });
    });
    it("Should have logged in", function () {
        this.timeout(20000);
        expect(browser.getTitle()).to.eventually.eq(app_title);
    });
    describe("Testing after login",function(){
        var proxy;
        before(function(){
            this.timeout(20000);
/*
            proxy=new backendProxy(browser);
            proxy.context={
                myvar:"2",
                coder:mockData.coderMap
            };
            proxy.onLoad.whenGET('/cloud/project/.+').respond(200, mockData.projects[0]);
            proxy.onLoad.whenGET('/cloud/project').respond(200, mockData.projects);
//            proxy.onLoad.whenGET('/cloud/coders').respond(200, mockData.coderMap);
            proxy.onLoad.whenGET('/cloud/coders').respond(function(method,url){
                $httpBackend.context.myvar="from the app";
                console.error( $httpBackend.context.myvar, "log!!");
                console.info("log!!", $httpBackend.context);
                console.warn("log!!");
                return [200,$httpBackend.context.coder];
            });
            proxy.onLoad.whenGET('/services/project').respond(200, mockData.services);
*/ //           proxy.onLoad.whenGET(/.*/).passThrough();
        });
        it("should call the get somehow",function(){
            this.timeout(2000000);
            browser.sleep(1).then(function(data){
                console.log("\n==========>getting page, here we go!!","\n");
//                browser.get(https_address+"/project/#/Overview");
                browser.executeAsyncScript(function(projects){
                    var cb=arguments[arguments.length-1];
                    var div=document.querySelector("div");
                    var modelServer=angular.element(div).injector().get("modelServer");
                    var getProject=modelServer.getProject;
                    console.info("mocking getProject....");
                    modelServer.getProject=function(){
                        console.info("getProject Called with->",projects);
                        return getProject.apply(modelServer,arguments);
                    };
                    cb("getProjectMocked!");
                },mockData.projects).then(function(data){
                    console.log("Async Script=======>",data,arguments);
//                    console.log("----->",proxy.context.myvar);
                });
            });
        });
        it("should sleep for a long time",function(){
                this.timeout(1000000);
                browser.sleep(120000);
        });
        it("should run next and clear the logs",function(){
            return browser.executeAsyncScript(function(callback){
                callback();
            }).then(function(){
                console.log("second call back!");
                browser.manage().logs().get('browser').then(function(browserLog) {
                    console.log("\n", "Log In test: ", util.inspect(browserLog) + "\n=========>end of log\n");
                });
            });
        });
        afterEach(function(){
            browser.manage().logs().get('browser').then(function(browserLog){
                console.log("\n","Log: ", util.inspect(browserLog)+"\n=========>end of log\n");
            });
        })
    })
});


xdescribe("Using Mock module to mock event cloud", function () {
    var page, header, login;
    before(function () {
        this.timeout(15000);
        console.log("before!");
        login = new LoginPage(https_address);
    });
    beforeEach(function () {
        this.timeout(15000);
        var proxy = new backendProxy(browser);
        proxy.onLoad.whenGET('/cloud/project/.+').respond(200, mockData.projects[0]);
        proxy.onLoad.whenGET('/cloud/project').respond(200, mockData.projects);
        proxy.onLoad.whenGET('/cloud/coders').respond(200, mockData.coderMap);
        proxy.onLoad.whenGET('/services/project').respond(200, mockData.services);
        proxy.onLoad.whenGET(/.*/).passThrough();
        return login.getPage().then(function () {
            console.log("before!, got page");
            return login.login(valid_user, valid_pass).then(function () {
                console.log("before!, logged in!");
                expect(browser.getTitle()).to.eventually.eq(app_title);
                page = new ProjectsPage();
            });
        })
    });
    it("Should call the mock server instead of modelserver", function () {
        browser.pause();
        expect(browser.getTitle()).to.eventually.eq(app_title);
    });
});
