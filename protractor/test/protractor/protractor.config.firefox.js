var HtmlReporter = require('protractor-html-screenshot-reporter');
var today = new Date();

var monthNames = [
        "January", "February", "March",
        "April", "May", "June", "July",
        "August", "September", "October",
        "November", "December"
    ];

var day = today.getDate();
var monthIndex = today.getMonth();
var month = ((today.getMonth()+1)>=10)? (today.getMonth()+1) : '0' + (today.getMonth()+1);
var year = today.getFullYear();

// console.log(day, monthNames[monthIndex], year);
// /usr/lib/apx-reporting/assets/reports/staging/progressreport/2015
// append a record to the following file:
// /usr/lib/apx-reporting/assets/progress_regression_reports_staging.txt
// "PR Regression Staging Report - April 23, 2015	reports/staging/progressreport/2015/4/23.html"
// /mnt/reports/staging/progressreport/'+year+'/'+month+'/'


//require('jasmine-reporters');
//require('mocha');
// jasmine.getEnv().addReporter(new jasmine.JUnitXmlReporter('outputdir/', true, true));

exports.config={
//	seleniumAddress:"http://localhost:4444/wd/hub",
	capabilities: {
        browserName: 'firefox'        
    },
    
    onPrepare: function() {
     var width = 1280;
     var height = 1024;
     //require('mocha');
     //require('jasmine-reporters');
     browser.ignoreSynchronization = true;
     browser.driver.manage().window().setSize(width, height);
     jasmine.getEnv().addReporter(new HtmlReporter({
         baseDirectory: '/usr/lib/apx-reporting/assets/reports/staging/progressreport/'+year+'/'+month+'/'
         , docName: day+'.html'
      }));
    },
       
	mochaOpts:{
		reporter:'spec',
		enableTimeouts:false
	},
	//framework:'mocha',
	specs:['specs/*.spec.js']  

}
