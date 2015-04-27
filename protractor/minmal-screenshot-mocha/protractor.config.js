exports.config={
	baseUrl:"http://localhost:9080/index.htm",
	framework:"mocha",
	specs:["*.spec.js"],
	seleniumAddress:"http://127.0.0.1:4444/wd/hub",
	plugins:[
		{
			path:"screenshot-plugin.js",
			picPath:"pics/"
		}
	]
};

