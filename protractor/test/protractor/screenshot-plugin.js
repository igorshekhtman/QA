/**
 * Created by rezaalemy on 15-04-20.
 */
 /**
 * Updated by Igor Shekhtman on 04-27-2015.
 */
var fs    = require("fs");
//var reportFolder = "reports"

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
    },
    
//========================================================================================
    teardown:function(config,passed,testInfo){
	//anything at the end of the session
	//for example, creating the final report and putting it in the right place
	
	
    },
    
//========================================================================================
    postResults:function(config,passed,testInfo){
    	//anything at the end of the suite
    	//copy created reports to backup folder
    	//append reports line if one does not already exist    	
    },
    
//========================================================================================
    postTest:function(config,passed,testInfo){
    //console.log(config['screenShotPath']);
    //console.log(config['reportPath']);
    //console.log(config);
    console.log(testInfo);
    
	if(!passed)
		return browser.takeScreenshot().then(function(png){
				var stream=fs.createWriteStream(""+config['screenShotPath']+"FailedTest.png");
				stream.write(new Buffer(png,"base64"));
				stream.end();		
		});
    },
    name:"protractor screenshot taker and report writer"
};
