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
     browser.ignoreSynchronization = true;
     browser.driver.manage().window().setSize(width, height);
     //jasmine.getEnv().addReporter(new HtmlReporter({
     //    baseDirectory: '/usr/lib/apx-reporting/assets/reports/staging/progressreport/'+year+'/'+month+'/'
     //    , docName: day+'.html'
     // }));
    },
       
	mochaOpts:{
		reporter:'spec',
		enableTimeouts:false
	},
	framework:'mocha',
	specs:['testsuite/*.spec.js'],
	//seleniumAddress:"http://10.250.164.225:39831/wd/hub",
	plugins:[
		{
			path:"screenshot-plugin.js",
			reportPath:"reports/",
			screenShotPath:"reports/"+String(day)+"/"
		}
	]  

}