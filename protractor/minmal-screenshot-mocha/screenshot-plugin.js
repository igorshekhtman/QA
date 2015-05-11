/**
 * Created by rezaalemy on 15-04-20.
 */
var fs=require("fs");

module.exports={
    setup:function(config){
	//anything at the start of the test
	//for example, create a directory for data and screenshots
    },
    teardown:function(config){
	//anything at the end of the session
	//for example, creating the final report and putting it in the right place
    },
    postResults:function(config){
    	//anything at the end of the suite
    },
    postTest:function(config,passed,testInfo){
	if(!passed)
		return browser.takeScreenshot().then(function(png){
				var stream=fs.createWriteStream("test3.png");
				stream.write(new Buffer(png,"base64"));
				stream.end();
		});
    },
    name:"protractor screenshot taker"
};
