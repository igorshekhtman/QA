/**
 * Created by rezaalemy on 15-04-05.
 */
var backendProxy = require("httpbackend"),
    mockData = require('./mockModel'),
    LoginPage = require("../pages/login"),
    valid_user = 'test1@apixio.net',
    valid_pass = 'zaq123',
    app_title = "Apixio Progress Report",
    https_address = "https://localhost:8643",
    expect   = require('chai').use(require('chai-as-promised')).expect;


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
        before(function(){
            this.timeout(20000);
            var proxy=new backendProxy(browser);
            proxy.whenGET('GET',/.*/).passThrough();
        });
        it("should call the get somehow",function(){
            this.timeout(20000);
            return browser.sleep(10000);
        });
    })
});
