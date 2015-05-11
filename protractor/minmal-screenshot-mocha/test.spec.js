var expect = require("chai").use(require("chai-as-promised")).expect;
describe("testing protractor",function(){
	it("should get the page",function(){
		browser.get("http://localhost:9080/index.htm");
	});
	it("should have a title",function(){
		expect(browser.getTitle()).to.eventually.equal("my title");
	});
});
