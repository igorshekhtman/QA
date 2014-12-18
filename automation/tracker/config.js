/**
 * Created by rezaalemy on 14-11-10.
 */
var args=require('minimist')(process.argv.slice(2));
var _=require('underscore');
//var fs=require('fs');
//var path=require('path');
var md = {
    debugMode:true,
    appPort:8038,
    appHost:'',
    appBase:function(){
        return this.appHost+':'+this.appPort;
    },
    maxInactivity:60000
};
function deepExtend(t,s){
    if(_.isArray(s))
        return s;
    else if(typeof s=='object')
        _.each(s,function(v,k){
            if(t[k])
                t[k]=deepExtend(t[k],v);
            else
                t[k]=v;
        });
    else
        return s;
    return t;
}
function configForProduction(){
    deepExtend(md,{});
}
function configForLocal(){
    console.log('running for local mode');
    md.appPort=3000;
    md.appHost='https://localhost';
    return md.appBase();
}
if(args.debug)
    console.log('running in debug mode');
if(args.local)
    configForLocal();
else
    configForProduction();
module.exports=md;