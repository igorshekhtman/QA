var express = require('express');
var _=require('underscore');
var router = express.Router();
var db=require('../model/model');

function handleRestError(err, next,status) {
    if (!err) err = new Error("Rest Service Error");
    err.status = status||504;
    next(err);
}
function displayObj(obj){
    if(_.isArray(obj))
        return [obj.length,displayObj(obj[0])];
    if(typeof obj!='object')
        return obj;
    var result=[];
    var i=0;
    _.each(obj,function(v,k){
        i+=1;
        if(i<5)
            result.push([k,displayObj(v)])
    });
    return result;
}
function callService(name,rest){
    var args=Array.prototype.slice.call(arguments,2);
    var req=rest[0];
    var res=rest[1];
    var next=rest[2];
    console.log.apply(console,["calling ",name].concat(args));
    if(!db[name])
        return handleRestError(new Error(name + ' is not implemented'),next,404);
    var promise=db[name].apply(db,args);
    if(promise.then)
        return promise.then(function(data){
            console.log(name,' resolved with ',displayObj(data),req.method);
            res.json(data);
        },function(err){
            console.log(name,' rejected with ',err);
            handleRestError(err,next);
        });
    console.log(name,' resolved with ',promise,req.method);
    return promise;
}

router.get('/',function(req,res){
    res.render('partials/main', { title: 'Apixio QA Dashboard',app:{name:'Tracker', official:'QA Dashboard'}
        ,user:req.user});
});
router.post('/api/announcement',function(req,res,next){
    callService('saveAnnouncement',arguments,req.body);
});
router.get('/api/announcement',function(req,res,next){
    callService('getAnnouncement',arguments);
});
router.delete('/api/announcement/:a_id',function(req,res,next){
    callService('deleteAnnouncement',arguments,req.params.a_id);
});
router.post('/api/admin_user',function(req,res,next){
    callService('saveAdminUser',arguments,req.body);
});
router.get('/api/admin_user',function(req,res,next){
    callService('getAdminUser',arguments);
});
router.delete('/api/admin_user/:a_id',function(req,res,next){
    callService('deleteAdminUser',arguments,req.params.a_id);
});
module.exports=router;