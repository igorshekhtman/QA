/**
 * Created by rezaalemy on 15-04-20.
 */
 /**
 * Updated by Igor Shekhtman on 04-27-2015.
 */
var fs    = require("fs");
//var reportFolder = "reports"
var report="";
var today = new Date();
var day = today.getDate();
var monthIndex = today.getMonth();
var month = ((today.getMonth()+1)>=10)? (today.getMonth()+1) : '0' + (today.getMonth()+1);
var year = today.getFullYear();

module.exports={

//========================================================================================
    setup:function(config,passed,testInfo){
	//anything at the start of the test
	//create a directories for reports and screenshots
	try { 
	    fs.mkdirSync(config['reportPath']); 
	    } 
	catch(e) {
        if ( e.code != 'EEXIST' ) throw e;
        }
     try { 
	    fs.mkdirSync(config['screenShotPath']); 
	    } 
	catch(e) {
        if ( e.code != 'EEXIST' ) throw e;
        }    
    
    // generate report header
    report = "";
	report = report + "<h1>Apixio Progress Report Test Results</h1>";
	//REPORT = REPORT + "Run date & time: <b>%s</b><br>\n" % (CUR_TIME)
	//REPORT = REPORT + "Report type: <b>%s</b><br>\n" % (REPORT_TYPE)
	//REPORT = REPORT + "Enviromnent: <b><font color='red'>%s%s</font></b><br>" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	//REPORT = REPORT + "OrgID: <b>%s</b><br>" % (ORGID)
	//REPORT = REPORT + "BatchID: <b>%s</b><br>" % (BATCHID)
	//REPORT = REPORT + "User name: <b>%s</b><br>" % (USERNAME)
	//REPORT = REPORT + "<table align='left' width='800' cellpadding='1' cellspacing='1'><tr><td>"
	report = report + "<table align='left' width='800' cellpadding='0' cellspacing='0' border='1'>";
	report = report + "<tr><td bgcolor='grey'><font color='white'>Description</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Passed</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Browser</td>";
	report = report + "<td bgcolor='grey'><font color='white'>OS</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Message</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Screenshot</td></tr>";
    
    },
//========================================================================================
    teardown:function(config,passed,testInfo){
	//anything at the end of the session
	//for example, creating the final report and putting it in the right place
	
	//console.log(report);
	report = report + "</table>";
	fs.writeFileSync(""+config['reportPath']+""+day+".html", report)
	
	
    },
    
//========================================================================================
    postResults:function(config,passed,testInfo){
    	//anything at the end of the suite
    	//copy created reports to backup folder
    	//append reports line if one does not already exist  
    	
    report = report +"<tr><td colspan='6'>"+testInfo['category']+"</td></tr>";	  	
    },
    
//========================================================================================
    postTest:function(config,passed,testInfo){
    //console.log(config['screenShotPath']);
    //console.log(config['reportPath']);
    //console.log(config);
    console.log(testInfo);
    report = report + "<tr><td bgcolor='white'><font color='black'>"+testInfo['name']+"</td>";
	report = report + "<td bgcolor='white'><font color='black'>"+passed+"</td>";
	report = report + "<td bgcolor='white'><font color='black'>firefox:31.6.0</td>";
	report = report + "<td bgcolor='white'><font color='black'>LINUX</td>";
	report = report + "<td bgcolor='white'><font color='black'>undefined</td>";
	report = report + "<td bgcolor='white'><font color='black'>View</td></tr>";
    
	if(!passed)
		return browser.takeScreenshot().then(function(png){
				var stream=fs.createWriteStream(""+config['screenShotPath']+"FailedTest.png");
				stream.write(new Buffer(png,"base64"));
				stream.end();		
		});
    },
    name:"protractor screenshot taker and report writer"
};
