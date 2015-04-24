exports.config={
//	seleniumAddress:"http://localhost:4444/wd/hub",
	capabilities: {
		'browserName': 'chrome'
	},
	framework:'mocha',
	specs:['mock/attic/pure-mock-protractor.specs.js'],
	baseUrl:"https://localhost:8643"
};
