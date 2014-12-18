/**
 * Created by rezaalemy on 14-12-17.
 */

var path=require('path');
var mango=require('./mango').open(path.resolve(__dirname,'../localDatabase.tingo'));
var _=require('underscore');
var md={};

md.saveAnnouncement=function(data){
    if(!_.isArray(data)) data=[data];
    var announcementCollection=mango.collection('Announcements');
    return announcementCollection.promise('insert',data).then(function(){
        return announcementCollection.promise('find');
    })
};
md.getAnnouncement=function(){
    var announcementCollection=mango.collection('Announcements');
    return announcementCollection.promise('find');
};
md.deleteAnnouncement=function(a_id){
    var announcementCollection=mango.collection('Announcements');
    return announcementCollection.promise('remove',{"_id":a_id},true);
};
md.saveAdminUser=function(data){
    if(!_.isArray(data)) data=[data];
    var announcementCollection=mango.collection('adminUsers');
    return announcementCollection.promise('insert',data).then(function(){
        return announcementCollection.promise('find');
    });
};
md.getAdminUser=function(){
    var announcementCollection=mango.collection('adminUsers');
    return announcementCollection.promise('find');
};
md.deleteAdminUser=function(a_id){
    var announcementCollection=mango.collection('adminUsers');
    return announcementCollection.promise('remove',{"_id":a_id},true);
};
module.exports=md;
