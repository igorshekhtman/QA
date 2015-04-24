exports.config={
//	seleniumAddress:"http://localhost:4444/wd/hub",
	capabilities: {
		'browserName': 'chrome'
	},
	mochaOpts:{
		reporter:'spec',
		enableTimeouts:false
	},
	framework:'mocha',
	specs:['specs/*.spec.js']
};
