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


	chromeOnly: false,
	
	capabilities: {
        browserName: 'firefox'        
    },
    
    onPrepare: function() {
    // 1920x1200
    // 1280x1024
    // var width = 1920;
    // var height = 1200;
     
     //global.isAngularSite = function(flag){
     //       browser.ignoreSynchronization = !flag;
     //};
      
    
     browser.ignoreSynchronization = true;
    // browser.driver.manage().window().setSize(width, height);
     
     browser.driver.manage().window().maximize();
     
     browser.getCapabilities().then(function (cap) {
  	 browser.browserName = cap.caps_.browserName;
  	 browser.browserVersion = cap.caps_.version;
	 });
     
     
    },
    
      
	mochaOpts:{
		reporter:'spec',
		slow:3000,
		enableTimeouts:false
	},
	framework:'custom',
	frameworkPath:'/usr/local/lib/node_modules/protractor/lib/frameworks/mocha-apixio.js',
	//framework:'mocha',
	
	//specs:['testsuite/*.spec.js'],
	specs:['specs/*.spec.js'],
	
	
	
	//seleniumAddress:"http://10.250.164.225:39831/wd/hub",
	
	
	//plugins:[
	//	{
	//		path:"mocha-report-with-screenshots-plugin.js",
			
	//		reportPath:"/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/",			
	//		backupPath:"/mnt/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/",
			
	//		reportFile:"/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html",
	//		backupReportFile:"/mnt/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html",
			
	//		screenShotFolder:"/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+"/",
	//		backupScreenShotFolder:"/mnt/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+"/",
			
			
			
	//		screenShotPath:"/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+"/",
	//		reportLine:"PR Regression Staging Report - "+monthNames[monthIndex]+" "+String(day)+", "+String(year)+"\treports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html\n",
	//		partReportLine:"reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html",
	//		reportTxtFolder:"/usr/lib/apx-reporting/assets/",
	//		reportTxtFname:"progress_regression_reports_staging.txt"
			
	//	}
	//]  

}