/***********************************************
 * Authors:  Reza Alamy and Igor Shekhtman
 *
 * Date: 05/14/2015
 *
 *
 ***********************************************/


var q = require('q');
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
var passed = 0;
var category="";


var	reportPath = "/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/";
var	backupPath = "/mnt/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/";
			
var reportFile = "/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html";
var backupReportFile = "/mnt/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html";
			
var screenShotFolder = "/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+"/";
var backupScreenShotFolder = "/mnt/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+"/";
			
			
			
var screenShotPath = "/usr/lib/apx-reporting/assets/reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+"/";
var reportLine = "PR Regression Staging Report - "+monthNames[monthIndex]+" "+String(day)+", "+String(year)+"\treports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html\n";
var partReportLine = "reports/staging/progressreport/"+String(year)+"/"+String(month)+"/"+String(day)+".html";
var reportTxtFolder = "/usr/lib/apx-reporting/assets/";
var reportTxtFname = "progress_regression_reports_staging.txt";

/**
 * Execute the Runner's test cases through Mocha.
 *
 * @param {Runner} runner The current Protractor Runner.
 * @param {Array} specs Array of Directory Path Strings.
 * @return {q.Promise} Promise resolved with the test results
 */
exports.run = function(runner, specs) {
  var Mocha = require('mocha'),
      mocha = new Mocha(runner.getConfig().mochaOpts);

  var deferred = q.defer();
  
  try { 
	    fs.mkdirSync(reportPath); 
	    } 
	catch(e) {
        if ( e.code != 'EEXIST' ) throw e;
        }
     try { 
	    fs.mkdirSync(screenShotPath); 
	    } 
	catch(e) {
        if ( e.code != 'EEXIST' ) throw e;
        }    
    // generate report header
    //report = "";
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


  // Mocha doesn't set up the ui until the pre-require event, so
  // wait until then to load mocha-webdriver adapters as well.
  mocha.suite.on('pre-require', function() {
    try {
      // We need to re-wrap all of the global functions, which selenium-webdriver/
      // testing only does when it is required. So first we must remove it from
      // the cache.
      delete require.cache[require.resolve('selenium-webdriver/testing')];
      var mochaAdapters = require('selenium-webdriver/testing');
      global.after = mochaAdapters.after;
      global.afterEach = mochaAdapters.afterEach;
      global.before = mochaAdapters.before;
      global.beforeEach = mochaAdapters.beforeEach;

      // The implementation of mocha's it.only uses global.it, so since that has
      // already been wrapped we must avoid wrapping it a second time.
      // See Mocha.prototype.loadFiles and bdd's context.it.only for more details.
      var originalOnly = global.it.only;
      global.it = mochaAdapters.it;
      global.it.only = global.iit = originalOnly;

      global.it.skip = global.xit = mochaAdapters.xit;
    } catch (err) {
      deferred.reject(err);
    }
  
  });

//----------------------------------------------------------------------------------------

  mocha.loadFiles();
 
//----------------------------------------------------------------------------------------  
	/**
     *  These are all the events you can subscribe to:
     *   - `start`  execution started
     *   - `end`  execution complete
     *   - `suite`  (suite) test suite execution started
     *   - `suite end`  (suite) all tests (and sub-suites) have finished
     *   - `test`  (test) test execution started
     *   - `test end`  (test) test completed
     *   - `hook`  (hook) hook execution started
     *   - `hook end`  (hook) hook complete
     *   - `pass`  (test) test passed
     *   - `fail`  (test, err) test failed
     */ 
     
 //----------------------------------------------------------------------------------------    

  runner.runTestPreparer().then(function() {

    specs.forEach(function(file) {
      mocha.addFile(file);
    });

    var testResult = [];

    var mochaRunner = mocha.run(function(failures) {
      try {
        if (runner.getConfig().onComplete) {
          runner.getConfig().onComplete();
        }
        deferred.resolve({
          failedCount: failures,
          specResults: testResult
        });
      } catch (err) {
        deferred.reject(err);
      }
    });
    
//----------------------------------------------------------------------------------------   

    mochaRunner.on('start', function(test) {
      console.log("Start of Test");
    
      // for some reason this one is not working ...
    
    });
    
//----------------------------------------------------------------------------------------

    mochaRunner.on('suite', function(test) {
      report = report + "<tr><td bgcolor='white' colspan='7'><font color='black'><b>"+test.fullTitle().slice(0, -test.title.length).trim()+"</b></td></tr>";
    });    

//----------------------------------------------------------------------------------------

    mochaRunner.on('pass', function(test) {
      var testInfo = {
        name: test.title,
        category: test.fullTitle().slice(0, -test.title.length).trim(),
        duration: test.duration,
        speed: test.speed,
        errorMsg: '',
        stackTrace: ''
      };
      runner.emit('testPass', testInfo);
      testResult.push({
        description: test.title,
        assertions: [{
          passed: true
        }],
        duration: test.duration
      });
      bgcolor = "green"
      total += 1;
      passed += 1;
      report = report + "<tr><td bgcolor='white'><font color='black'>"+String(total)+"</td>";
      report = report + "<td bgcolor='white'><font color='black'>"+testInfo['name']+"</td>";
	  report = report + "<td bgcolor="+bgcolor+"><font color='white'>true</td>";
	  report = report + "<td bgcolor='white'><font color='black'>("+testInfo['duration']+"ms)</td>";
	  report = report + "<td bgcolor='white'><font color='black'>"+browser.browserName+" "+browser.browserVersion+"</td>";
      report = report + "<td bgcolor='white'><font color='black'>"+testInfo['errorMsg']+"</td>";
	  report = report + "<td bgcolor='white'><font color='black'></td></tr>";	
    });

//----------------------------------------------------------------------------------------

    mochaRunner.on('fail', function(test) {
      var testInfo = {
        name: test.title,
        category: test.fullTitle().slice(0, -test.title.length).trim(),
        duration: test.duration,
        speed: test.speed,
        errorMsg: test.err.message,
        stackTrace: test.err.stack
      };
      runner.emit('testFail', testInfo);
      testResult.push({
        description: test.title,
        assertions: [{
          passed: false,
          errorMsg: test.err.message,
          stackTrace: test.err.stack
        }],
        duration: test.duration
      });
      bgcolor = "red";
      total += 1;
      failed += 1;
      report = report + "<tr><td bgcolor='white'><font color='black'>"+String(total)+"</td>";
      report = report + "<td bgcolor='white'><font color='black'>"+testInfo['name']+"</td>";
	  report = report + "<td bgcolor="+bgcolor+"><font color='white'>false</td>";
	  report = report + "<td bgcolor='white'><font color='black'>("+testInfo['duration']+"ms)</td>";
	  report = report + "<td bgcolor='white'><font color='black'>"+browser.browserName+" "+browser.browserVersion+"</td>";
      report = report + "<td bgcolor='white'><font color='black'>"+testInfo['errorMsg']+" <a href="+String(day)+"/"+String(total)+".html target='_self'>View Stack Trace Info</a></td>";
	  report = report + "<td bgcolor='white'><font color='black'><a href="+String(day)+"/"+String(total)+".png target='_self'>View</a></td></tr>";
	  // create and save stack trace info html file
	  fs.writeFile(""+screenShotPath+""+String(total)+".html", testInfo['stackTrace'], function (err) {
  		  if (err) throw err;
  		//console.log('Stack trace report file is saved...');
	  });
	  return browser.takeScreenshot().then(function(png){
				var stream=fs.createWriteStream(""+screenShotPath+""+String(total)+".png");
				stream.write(new Buffer(png,"base64"));
				stream.end();		
	  });
      
    });
    
//----------------------------------------------------------------------------------------
    
    mochaRunner.on('test end', function(test) {    
      //total += 1;
      //bgcolor = "green"
 
    });

//----------------------------------------------------------------------------------------
    
    mochaRunner.on('end', function(test) {
      console.log("End of Test Suite");
      
            
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
	

		
	  fs.writeFile(""+reportPath+""+day+".html", report, function (err) {
  	  	if (err) throw err;
  		console.log('Test report file is saved...');
	  });
	
	  // appending report line to txt file if does not already exist
	  fs.readFile(""+reportTxtFolder+""+reportTxtFname+"", 'ascii', function (err,data) {
  		if (err) {
    	return console.log(err);
  		}
  		//console.log(data);
  		if(data.indexOf(partReportLine) > -1)
  			console.log("Report entry line exists, skipping ...");
  		else {
  			console.log("Report entry line does not exist, appending ...");	
  			fs.appendFile(""+reportTxtFolder+""+reportTxtFname+"", reportLine, function (err) {
				if (err) throw err;
  				console.log('New report line was appended to report txt file...');
			});	
  		}
	  });
	
	  // backup report file to mnt drive
	  exec("cp -avu "+reportFile+" "+backupReportFile+"", function(error, stdout, stderr) {
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
	exec("cp -avru "+screenShotFolder+" "+backupScreenShotFolder+"", function(error, stdout, stderr) {
        console.log("stdout: " + stdout);
        console.log("stderr: " + stderr);
        if(error !== null) {
            console.log("exec error: " + error);
        } 
        else {
			console.log("Report file backed up...");
        }
    });   
      
      
         
    });
    
 //----------------------------------------------------------------------------------------   
    
    
  }).catch (function(reason) {
      deferred.reject(reason);
  });

  

  return deferred.promise;
};
