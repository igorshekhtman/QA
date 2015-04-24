var HtmlReporter = require('protractor-html-screenshot-reporter');

exports.config={
//	seleniumAddress:"http://localhost:4444/wd/hub",
	capabilities: {
        browserName: 'phantomjs'        
    },
    
    onPrepare: function () {
      var width = 1280;
      var height = 1024;
      browser.ignoreSynchronization = true;
      browser.driver.manage().window().setSize(width, height);
      jasmine.getEnv().addReporter(new HtmlReporter({
        baseDirectory: '/tmp/screenshots'
      }));
    },
    
    
	mochaOpts:{
		reporter:'spec',
		enableTimeouts:false
	},
	framework:'mocha',
	specs:['specs/*.spec.js']
};