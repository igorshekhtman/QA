/**
 * Created by rezaalemy on 14-12-17.
 */
var mango=require('../model/mango');
var should=require('should');

describe("testing promise implemnetation of tingo",function(){
    var col;
    before(function(){
        var db=mango.open('testDatabase.tingo');
        col=db.collection("announcements");
        col.promise.should.be.ok;
    });
    it("should open a collection in the database",function(){
        return col.promise('insert'
            ,[
                {announcement:'announcement 1',madeBy:'reza@alemy.net',at:new Date().getTime()},
                {announcement:'announcement 2',madeBy:'reza@alemy.net',at:new Date().getTime()},
                {announcement:'announcement 3',madeBy:'reza@alemy.net',at:new Date().getTime()}
            ]).then(function(data){
               console.log(data);
            },function(err){
               console.log(err);
            });
    });
});