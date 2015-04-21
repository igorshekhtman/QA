var expect = require('chai').use(require('chai-as-promised')).expect;

describe("Testing Progress Report",function (){
	var user;
	it("Should go to login page",function(){
		browser.get("https://progressreport-stg.apixio.com");
		expect(browser.getTitle()).to.eventually.equal("Apixio Login Page");		
	});
	it("Should have a username input in the login page",function(){
		user=element(by.css("input.form-control[name='username']"));
		expect(user.isPresent()).to.eventually.be.ok;
	});
	it("Should be able to type username in the input",function(){
		return user.sendKeys("reza and igor").then(function(){
			expect(user.getAttribute("value")).to.eventually.equal("reza and igor");
		});
	});
	it("should be able to click on the login buton",function(){
		this.timeout(10000);
		return element(by.css("input.btn[type='submit']")).click().then(function(){
			expect(user.getAttribute("value")).to.eventually.equal("");
		});
	});
});

