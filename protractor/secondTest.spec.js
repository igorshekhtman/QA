var expect = require('chai').use(require('chai-as-promised')).expect;

describe("Testing HCC Application",function (){
	var user;
	var pwd;
	var user_controls;
	var logout_button;
	it("Should go to login page",function(){
		browser.ignoreSynchronization=true;
		browser.get("https://hccstage2.apixio.com/account/login");
		expect(browser.getTitle()).to.eventually.equal("Apixio HCC Optimizer");		
	});
	it("Should have a username input in the login page",function(){
		user=element(by.css("input.form-control[name='username']"));
		expect(user.isPresent()).to.eventually.be.ok;
	});
	it("Should have a password input in the login page",function(){
		pwd=element(by.css("input.form-control[name='password']"));
		expect(pwd.isPresent()).to.eventually.be.ok;
	});
	it("Should be able to type username in the input",function(){
		return user.sendKeys("sanitytest001@apixio.net").then(function(){
			expect(user.getAttribute("value")).to.eventually.equal("sanitytest001@apixio.net");
		});	
	});
	it("Should be able to type password in the input",function(){
		return pwd.sendKeys("apixio.123").then(function(){
			expect(pwd.getAttribute("value")).to.eventually.equal("apixio.123");
		});	
	});
	it("should be able to click on the login buton",function(){
		this.timeout(20000);
		return element(by.css("input.btn[name='login']")).click().then(function(){
			expect(browser.getTitle()).to.eventually.equal("HCC 4.1.2");
		});
	});
	it("should have user controls in the HCC Application page",function(){
		user_controls=element(by.xpath("html/body/div[1]/div[1]/div[2]/user-controls/span"));
		expect(user_controls.isPresent()).to.eventually.be.ok;
	});	
	
	it("should be able to click on the user controls",function(){
		return user_controls.click().then(function(){
			expect(browser.getTitle()).to.eventually.equal("HCC 4.1.2");
		});
	});
	it("should have Logout button present",function(){
		logout_button=element(by.xpath("html/body/div[1]/div[1]/div[2]/ul/li[5]/a"));
		expect(logout_button.isPresent()).to.eventually.be.ok;
	});	
	
	it("should be able to click on the logout button",function(){
		return logout_button.click().then(function(){
			expect(browser.getTitle()).to.eventually.equal("Apixio HCC Optimizer");
		});
	});
	
	
});

