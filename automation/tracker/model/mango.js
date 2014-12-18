/**
 * Created by rezaalemy on 14-12-17.
 */
var engine=require('tingodb')().Db;
var q=require('q');
var _=require('underscore');

var specials={
    find:function(collection,cb,args){
        collection.find.apply(collection,args).toArray(cb);
    }
};
function convertToPromise(collection,command,defer,args){
    if(!collection[command])
        return defer.reject(new Error('No such Database command: '+command));
    var cb=function(err,result){
        if(err)
            defer.reject(new Error('Error in '+command+'with args'+args))
        else
            defer.resolve(result);
    };
    if(specials[command])
        return specials[command](collection,cb,args);
    args.push(cb);
    collection[command].apply(collection,args);
}
function collection(reference){
    this.reference=reference;
}
collection.prototype={
    find:function(){
      return this.reference.find.apply(this.reference,arguments);
    },
    promise:function(command){
        var defer= q.defer();
        var args=Array.prototype.slice.call(arguments,1);
        convertToPromise(this.reference,command,defer,args);
        return defer.promise;
    }
};
function helper(db){
    this.db=db;
}
helper.prototype={
    collection:function(collectionName){
        return new collection(this.db.collection(collectionName));
    }
};
var helpers={};
md={
    open:function(dbName){
        if(!helpers[dbName])
            helpers[dbName]=new helper(new engine(dbName,{}));
        return helpers[dbName];
    }
};
module.exports=md;
