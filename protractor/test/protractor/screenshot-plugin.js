/**
 * Created by rezaalemy on 15-04-20.
 */
 /**
 * Updated by Igor Shekhtman on 04-27-2015.
 */
var fs    = require("fs");
//var reportFolder = "reports"

module.exports={
    setup:function(config,passed,testInfo){
	//anything at the start of the test
	//for example, create a directory for data and screenshots
	try {
      fs.mkdirSync(config['reportPath']);
      } catch(e) {
      if ( e.code != 'EEXIST' ) throw e;
      }
    },
    teardown:function(config,passed,testInfo){
	//anything at the end of the session
	//for example, creating the final report and putting it in the right place
    },
    postResults:function(config,passed,testInfo){
    	//anything at the end of the suite
    },
    postTest:function(config,passed,testInfo){
    
	if(!passed)
		console.log(config['reportPath'])
		return browser.takeScreenshot().then(function(png){
				var stream=fs.createWriteStream(""+config['reportPath']+"FailedTest.png");
				stream.write(new Buffer(png,"base64"));
				stream.end();
		});
    },
    name:"protractor screenshot taker and report writer"
};
