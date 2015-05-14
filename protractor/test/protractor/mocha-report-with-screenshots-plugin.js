 /**
 * Updated by Igor Shekhtman on 04-27-2015.
 */
var fs    = require("fs");
var exec = require("exec");
var os = require("os");
//var useragent = require('useragent');
var report="";
var today = new Date();
var start_time = new Date();
var day = today.getDate();
var monthIndex = today.getMonth();
var month = ((today.getMonth()+1)>=10)? (today.getMonth()+1) : '0' + (today.getMonth()+1);
var year = today.getFullYear();
var total = 0;
var failed = 0;
var category="";

module.exports={

//========================================================================================
    setup:function(config){
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
    report = report + "<table align='left' width='800' cellpadding='0' cellspacing='0' border='0'>"
    report = report + "<r><td><h1>Apixio Progress Report Test Results</h1></td></tr>";
	report = report + "<r><td><b>Operating System:</b> "+String(os.type()).toUpperCase()+"<br><br></td></tr>";
	
	
	report = report + "<tr><td>";
	
	
	
	report = report + "<table align='left' width='800' cellpadding='3' cellspacing='0' border='1'>";
	report = report + "<tr><td bgcolor='grey'><font color='white'>TC#</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Description</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Passed</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Duration</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Browser</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Message</td>";
	report = report + "<td bgcolor='grey'><font color='white'>Screenshot</td></tr>";
    
    },
//========================================================================================
    teardown:function(config){
	  //anything at the end of the session
	  //for example, creating the final report and putting it in the right place
		
    },
    
//========================================================================================
    postResults:function(config){
    	//anything at the end of the suite
    	//copy created reports to backup folder
    	//append reports line if one does not already exist  
     //anything at the end of the session
	  //for example, creating the final report and putting it in the right place
	
	  //console.log(report);
	  var duration = start_time - new Date();
	  //var duration = moment.duration((start_time - new Date()), "minutes").format("h:mm");
	
	  // generate report footer
	  report = report + "</table></td></tr>";
	  report = report + "<tr><td><br><h1><u>Results summary</u></h1></td></tr>";
	  report = report + "<tr><td><b>Total tests passed:</b> "+String(total-failed)+"</td></tr>";
	  report = report + "<tr><td><b>Total tests failed:</b> "+String(failed)+"</td></tr>";
	  report = report + "<tr><td><b>Total tests executed:</b> "+String(total)+"</td></tr>";
	  report = report + "<tr><td>This report generated on "+today+"</td></tr>";
	  //report = report + "<tr><td>Test duration was "+duration+"</td></tr>";
	  report = report + "</table>";
	

		
	  fs.writeFile(""+config['reportPath']+""+day+".html", report, function (err) {
  	  	if (err) throw err;
  		console.log('Test report file is saved...');
	  });
	
	  // appending report line to txt file if does not already exist
	  fs.readFile(""+config['reportTxtFolder']+""+config['reportTxtFname']+"", 'ascii', function (err,data) {
  		if (err) {
    	return console.log(err);
  		}
  		//console.log(data);
  		if(data.indexOf(config['partReportLine']) > -1)
  			console.log("Report entry line exists, skipping ...");
  		else {
  			console.log("Report entry line does not exist, appending ...");	
  			fs.appendFile(""+config['reportTxtFolder']+""+config['reportTxtFname']+"", config['reportLine'], function (err) {
				if (err) throw err;
  				console.log('New report line was appended to report txt file...');
			});	
  		}
	  });
	
	  // backup report file to mnt drive
	  exec("cp -avu "+config['reportFile']+" "+config['backupReportFile']+"", function(error, stdout, stderr) {
        console.log("stdout: " + stdout);
        console.log("stderr: " + stderr);
        if(error !== null) {
            console.log("exec error: " + error);
        } 
        else {
			console.log("Report file backed up...");
        }
    });
	
	
	// backup screen-shot folder to mnt drive
	exec("cp -avru "+config['screenShotFolder']+" "+config['backupScreenShotFolder']+"", function(error, stdout, stderr) {
        console.log("stdout: " + stdout);
        console.log("stderr: " + stderr);
        if(error !== null) {
            console.log("exec error: " + error);
        } 
        else {
			console.log("Report file backed up...");
        }
    });   	
   
	
   	  	
    },
    
//========================================================================================
    postTest:function(config,passed,testInfo){
    //console.log(config['screenShotPath']);
    //console.log(config['reportPath']);
    //console.log(config);
    //console.log(testInfo);
    total += 1;
    bgcolor = "green"
    if(!passed) {
    	bgcolor = "red";
    	failed += 1;
        }
    if (testInfo['category'] != category) {
          report = report + "<tr><td bgcolor='white' colspan='7'><font color='black'><b>"+testInfo['category']+"</b></td></tr>";
          category = testInfo['category'];
          }
    // generate report details      
    report = report + "<tr><td bgcolor='white'><font color='black'>"+String(total)+"</td>";
    report = report + "<td bgcolor='white'><font color='black'>"+testInfo['name']+"</td>";
	report = report + "<td bgcolor="+bgcolor+"><font color='white'>"+passed+"</td>";
	report = report + "<td bgcolor='white'><font color='black'>("+testInfo['duration']+"ms)</td>";
	report = report + "<td bgcolor='white'><font color='black'>"+browser.browserName+" "+browser.browserVersion+"</td>";
	//report = report + "<td bgcolor='white'><font color='black'>"+testInfo['errorMsg']+" <a href='' target='_blank'>View Stack Trace Info</a></td>";
	

	
	if(!passed) {
		report = report + "<td bgcolor='white'><font color='black'>"+testInfo['errorMsg']+" <a href="+String(day)+"/"+String(total)+".html target='_self'>View Stack Trace Info</a></td>";
		report = report + "<td bgcolor='white'><font color='black'><a href="+String(day)+"/"+String(total)+".png target='_self'>View</a></td></tr>";
		// create and save stack trace info html file
		fs.writeFile(""+config['screenShotPath']+""+String(total)+".html", testInfo['stackTrace'], function (err) {
  			if (err) throw err;
  			//console.log('Stack trace report file is saved...');
		});
		
		
		
		}
	else {
		report = report + "<td bgcolor='white'><font color='black'>"+testInfo['errorMsg']+"</td>";
		report = report + "<td bgcolor='white'><font color='black'></td></tr>";	
		}
    // generate and save screen-shot as well as the stack trace info html page
	if(!passed)
		return browser.takeScreenshot().then(function(png){
				var stream=fs.createWriteStream(""+config['screenShotPath']+""+String(total)+".png");
				stream.write(new Buffer(png,"base64"));
				stream.end();		
		});
    },
    name:"protractor screenshot taker and report writer"
};
