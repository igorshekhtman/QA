/**
 * Created by rezaalemy on 14-12-16.
 */
window.versionString='V 1.0.258 last build: Tue 25 Nov 2014 10:54:22 PST';
var tracker=angular.module('Tracker',['ApixioReusableModules','ngSanitize','ui.bootstrap']);
tracker.controller('topLevel',['$scope','$rootScope','restService'
, function ($scope,$rootScope,restService) {
        $scope.mainTabs = {
            tabs: [
                {name: 'home', content: 'Home'},
                {name: 'env', content: 'Environment Status'},
                {name: 'envSetup', content: 'Environment Setup'},
                {name: 'testCases', content: 'Test Case Selection'},
                {name: 'run', content: 'Run'},
                {name: 'runStatus', content: 'Run Status'},
                {name: 'reports', content: 'Run Reports'},
                {name: 'jira', content: 'Jira'}
            ], activeTab: 'home'
        };
        $rootScope.buildString = window.versionString;
    }])
    .controller('home',['$scope','restService',function($scope,restService){
        $scope.title='Home Page';
        function mapAnnouncements(data){
            return _.map(_.sortBy(data,'at').reverse(),function(announcement){
                announcement.at= new Date(announcement.at).toLocaleString();
                return announcement;
            });
        }
        function getAnnouncements(){
            restService.callService('getAnnouncement').then(function(data){
                $scope.Announcements= mapAnnouncements(data);
            });
        }
        $scope.saveAnnouncement=function(user){
            var msg= $scope.newAnnouncement.trim();
            if(!msg) return;
            var data={msg:msg,by:user,at:new Date()};
            restService.callService('saveAnnouncement',data).then(function(data){
                $scope.Announcements= mapAnnouncements(data);
                $scope.newAnnouncement='';
            });
        };
        $scope.deleteAnnouncement=function(id){
            restService.callService('deleteAnnouncement',id).then(function(){
                getAnnouncements();
            });
        };
        function mapAdminUsers(data){
            return _.sortBy(data,'email');
        }
        function getAdminUsers(){
            restService.callService('getAdminUser').then(function(data){
                $scope.adminUsers= mapAdminUsers(data);
            });
        }
        $scope.saveAdminUser=function(){
            var msg= $scope.newAdminUser.trim();
            if(!msg) return;
            var data={email:msg};
            restService.callService('saveAdminUser',data).then(function(data){
                $scope.adminUsers= mapAdminUsers(data);
                $scope.newAdminUser='';
            });
        };
        $scope.deleteAdminUser=function(id){
            restService.callService('deleteAdminUser',id).then(function(){
                getAdminUsers();
            });
        };
        getAnnouncements();
        getAdminUsers();
    }])
    .controller('env',['$scope',function($scope){
        $scope.title="Environments Page. this shows the environments and their health";
    }])
    .controller('envSetup',['$scope',function($scope){
        $scope.title="Environment Setup page. this is the place to define and set environment parameters";
    }])
    .controller('testCases',['$scope',function($scope){
        $scope.title="Test cases page. here we define test cases to run in each environment";
    }])
    .controller('run',['$scope',function($scope){
        $scope.title="Run Page. this is where tests are started";
    }])
    .controller('runStatus',['$scope',function($scope){
        $scope.title="Run Status Page. the status of running tests";
    }])
    .controller('reports',['$scope',function($scope){
        $scope.title="Reports Page. this is where we see the reports of the tests that have run";
    }])
    .controller('Jira',['$scope',function($scope){
        $scope.title="Jira Page. this is where we integrate JIRA";
    }])
    .factory('restService',['$ApixioRestClient',function(client){
    var restCallOpts={
        saveAnnouncement:function(data){
            return {url:'/api/announcement',method:'POST',data:data};
        },
        getAnnouncement:function(){
            return {url:'/api/announcement'};
        },
        deleteAnnouncement:function(id){
            return {url:'/api/announcement/'+id,method:"DELETE"};
        },
        saveAdminUser:function(data){
            return {url:'/api/admin_user',method:'POST',data:data};
        },
        getAdminUser:function(){
            return {url:'/api/admin_user'};
        },
        deleteAdminUser:function(id){
            return {url:'/api/admin_user/'+id,method:"DELETE"};
        }

    };
    return {
        callService:function(endpoint){
            var args=Array.prototype.slice.call(arguments,1);
            var opts={sendProtocol:'json'};
            if(restCallOpts[endpoint])
                opts= window.jQuery.extend(opts,
                    restCallOpts[endpoint].apply(this,args));
            return client.restCall(opts).then(function(data){
                if(!opts.reportProgress)
                    return data;
                return client.reportProgress({url:opts.reportProgress,id:data.id
                    ,shouldReject:function(data){
                        return _.find(data.inspect,function(s){
                            return s.state=='rejected';
                        });
                    }});
            });
        }
    }
}]);
