/**
 * Created by rezaalemy on 2014-09-30.
 */
angular.module('ApixioReusableModules',[])
    .factory('$ApixioRestClient', function ($http, $q, $rootScope, $timeout) {
        var mock;
        return {
            initMock:function(mockProvider){
                mock=mockProvider;
            },
            restCall: function (options) {
                var deferred = $q.defer();
                var opts = $.extend({}, {method: "GET",headers:{'X-Requested-With':'XMLHttpRequest'}}, options);
                var setHeadersAsFormSubmit = function (opts) {
                    if (opts.method == 'POST' || opts.method == 'PUT') {
                        if(!opts.headers) opts.headers={};
                        opts.headers['Content-Type']= 'application/x-www-form-urlencoded';
                        if (opts.data)
                            opts.data = $.param(opts.data);
                    }
                };
                var mockTheCall = function (opts) {
                    mock[opts.mockCall].apply(mock, [opts].concat(opts.arguments));
                    deferred.resolve(opts.mockResult);
                    console.log('mocked', opts.mockCall, opts.url, opts.method, opts.mockResult, opts.data);
                    return deferred.promise;
                };
                if (!opts.sendProtocol)
                    setHeadersAsFormSubmit(opts);
                if (opts.mockCall)
                    if(mock)
                        return mockTheCall(opts);
                $http(opts).success(function (data) {
                    deferred.resolve(data);
                    $rootScope.restServiceError='';
                }).error(function (data) {
                    deferred.reject(data);
                    $rootScope.restServiceError = data;
                });
                return deferred.promise;
            }
            ,reportProgress: function(options){
                var deferred=$q.defer();
                var opts={method:'GET'
                    ,url:options.url+options.id
                    ,shouldResolve:options.shouldResolve||function(data){
                        return data.done >= data.total;
                    }
                    ,shouldReject:options.shouldReject||function(){
                        return false;
                    }};
                function getNextProgress(){
                    $http(opts).then(function(data){
                        if(opts.shouldResolve(data.data))
                            return deferred.resolve(data.data);
                        if(opts.shouldReject(data.data))
                            return deferred.reject(data.data);
                        else
                            $timeout(getNextProgress,1000);
                        deferred.notify(data.data);
                    });
                }
                if(options.mockCall)
                    deferred.resolve({done:100,total:100});
                else
                    getNextProgress();
                return deferred.promise;
            }
        }
    })
    .factory('$ApixioXMLReader', function ($ApixioRestClient) {
        return {
            readXML: function (options) {
                return $ApixioRestClient.restCall(options).then(function (data) {
                    return (new DOMParser()).parseFromString(data.data, 'text/xml');
                });
            }
        }
    })
    .filter('uniqueKeys', function () {
        return function (input, key) {
            var keys = {};
            var retVal = [];
            input.forEach(function (inp) {
                if (keys[inp[key]]) return;
                retVal.push(inp[key]);
                keys[inp[key]] = 1;
            });
            return retVal;
        }
    })
    .filter('filterOnKey', function () {
        return function (input, key, value) {
            var retVal = [];
            input.forEach(function (inp) {
                if (inp[key] === value)
                    retVal.push(inp);
            });
            return retVal;
        }
    })
    .filter('removeIfPresent', function () {
        return function (input, reference, key) {
            return _.filter(input, function (item) {
                return !_.find(reference, function (ref) {
                    if (key)
                        return ref[key] == item[key];
                    return ref == item;
                });
            });
        };
    })
    .directive('stopEvent', function () {
        return function (scope, element, attr) {
            element.bind('click', function (e) {
                e.stopPropagation();
                e.preventDefault();
            });
        };
    })
    .directive('nxEqualEx', function () {
        return {
            require: 'ngModel',
            link: function (scope, elem, attrs, model) {
                if (!attrs.nxEqualEx) {
                    console.error('nxEqualEx expects a model as an argument!');
                    return;
                }
                scope.$watch(attrs.nxEqualEx, function (value) {
                    // Only compare values if the second ctrl has a value.
                    if (model.$viewValue !== undefined && model.$viewValue !== '') {
                        model.$setValidity('nxEqualEx', value === model.$viewValue);
                    }
                });
                model.$parsers.push(function (value) {
                    // Mute the nxEqual error if the second ctrl is empty.
                    if (value === undefined || value === '') {
                        model.$setValidity('nxEqualEx', true);
                        return value;
                    }
                    var isValid = value === scope.$eval(attrs.nxEqualEx);
                    model.$setValidity('nxEqualEx', isValid);
                    return isValid ? value : undefined;
                });
            }
        };
    })
    .directive('chevron', function () {
        return{
            transclude: true, scope: {
                order: "=chevron", direction: '=', by: '@'
            }, template: '<a href="" ng-click="order=by;direction=!direction" ng-transclude ></a><span ng-show="order==by"> ' +
                '<span ng-show="direction" class="glyphicon glyphicon-chevron-down"></span>' +
                '<span ng-hide="direction" class="glyphicon glyphicon-chevron-up"></span>' +
                '</span>'
        }
    })
    .directive('requester', function ($compile) {
        return{
            transclude: true,
            scope: {
                requester: '@'
            },
            template: '<span data-toggle="modal" data-target="{{requester}}" ng-transclude ></span>'
        };
    })
    .directive('tabNav',function($compile){
        return{
            scope:{
                tabNav:'='
            }
            ,controller:function($scope){
                this.renderTabList=function(tabNav){
                    var template=_.reduce(tabNav.tabs,function(memo,tab){
                        var plus='';
                        if(tab.plus)
                            plus=' plus="tabNav.prep'+tab.name+'()" plus-target="'+tab.plus+'"'
                        return memo+='<li tab-list="tabNav.activeTab" tab-name="'+tab.name+'"'+plus+'>'+tab.content+'</li>';
                    },'<ul class="nav nav-tabs">')+'</ul>';
                    return $compile(template)($scope);
                }
            }
            ,link:function(scope,el,attrs,ctrl){
                scope.$watch(function(){return scope.tabNav.tabs.length+scope.tabNav.activeTab;},function(o,n){
                    if(!n) return true;
                    el.empty();
                    el.append(ctrl.renderTabList(scope.tabNav))
                    return true;
                });
            }
        }
    })
    .directive('tabList', function () {
        return{
            transclude: true, scope: {
                tabList: '=', tabName: "@", plus: '&', plusTarget: '@'
            }, template: function (tElem, tAttrs) {
                var base = '<a href="javascript:void(0);" ng-click="tabList=tabName"><span ng-transclude></span> ';
                if (tAttrs.plus)
                    base +=
                        "<span ng-click='plus()' stop-event data-toggle='modal' " +
                        "data-target='{{plusTarget}}' ng-show='tabList==tabName' " +
                        "class='glyphicon glyphicon-plus'></span> ";
                return base + '</a>'
            }, link: function (scope, element) {
                scope.$watch('tabList', function (newValue) {
                    if (newValue == scope.tabName)
                        element.addClass('active');
                    else
                        element.removeClass('active');
                })
            }
        }
    })
    .config(function ($httpProvider) {
        $httpProvider.responseInterceptors.push('apixioSpinnerInterceptor');
        $httpProvider.defaults.transformRequest.push(function (data,headerGetter) {
            if(!headerGetter()['X-no-spinny'])
                $('div#spinner').show();
            return data;
        });
    })
    .factory('apixioSpinnerInterceptor', function ($q) {
        return function (promise) {
            return promise.then(function (response) {
                $('div#spinner').hide();
                return response;
            }, function (response) {
                $('div#spinner').hide();
                return $q.reject(response);
            });
        };
    })
    .constant('xmlEditorConfig', {
        codemirror: {
            mode: 'xml', lineNumbers: true, extraKeys: {
                "Ctrl-Space": "autocomplete", "'<'": function (cm) {
                    return window.apixioXMLAutoComplete.completeAfter(cm);
                }, "'/'": function (cm) {
                    return window.apixioXMLAutoComplete.completeIfAfterLt(cm);
                }, "' '": function (cm) {
                    return window.apixioXMLAutoComplete.completeIfInTag(cm);
                }, "'='": function (cm) {
                    return window.apixioXMLAutoComplete.completeIfInTag(cm, "=");
                }

            }
        }
    })
    .factory('downloadContent',function(){
        return{
            download:function(data,contentType,fileName){
                var el=angular.element('<a/>').attr({href:contentType+encodeURI(data)
                    ,target:'_blank'
                    ,download:fileName})[0];
                var ev=document.createEvent('MouseEvents');
                ev.initMouseEvent('click',true,true,window,1,0,0,0,0,false,false,false,false,0,null);
                el.dispatchEvent(ev);
            }
        }
    })
    .directive('uiCodemirror', ['xmlEditorConfig', 'xmlEditorSchema', function (uiCodemirrorConfig, hintOptions) {
        return {
            restrict: 'EA',
            require: '?ngModel',
            priority: 1,
            compile: function compile() {
// Require CodeMirror
                if (angular.isUndefined(window.CodeMirror)) {
                    throw new Error('ui-codemirror need CodeMirror to work... (o rly?)');
                }
                return function postLink(scope, iElement, iAttrs, ngModel) {
                    var options, opts, codeMirror, initialTextValue;
                    initialTextValue = iElement.text();
                    options = uiCodemirrorConfig.codemirror || {};
                    options.hintOptions = angular.extend({}, options.codemirror, hintOptions);
                    opts = jQuery.extend(true, { value: initialTextValue }, options, scope.$eval(iAttrs.uiCodemirror), scope.$eval(iAttrs.uiCodemirrorOpts));
                    if (iElement[0].tagName === 'TEXTAREA') {
// Might bug but still ...
                        codeMirror = window.CodeMirror.fromTextArea(iElement[0], opts);
                    } else {
                        iElement.html('');
                        codeMirror = new window.CodeMirror(function (cm_el) {
                            iElement.append(cm_el);
                        }, opts);
                    }
                    if (iAttrs.uiCodemirror || iAttrs.uiCodemirrorOpts) {
                        var codemirrorDefaultsKeys = Object.keys(window.CodeMirror.defaults);
                        scope.$watch(iAttrs.uiCodemirror || iAttrs.uiCodemirrorOpts, function updateOptions(newValues, oldValue) {
                            if (!angular.isObject(newValues)) {
                                return;
                            }
                            codemirrorDefaultsKeys.forEach(function (key) {
                                if (newValues.hasOwnProperty(key)) {
                                    if (oldValue && newValues[key] === oldValue[key]) {
                                        return;
                                    }
                                    codeMirror.setOption(key, newValues[key]);
                                }
                            });
                        }, true);
                    }
                    if (ngModel) {
// CodeMirror expects a string, so make sure it gets one.
// This does not change the model.
                        ngModel.$formatters.push(function (value) {
                            if (angular.isUndefined(value) || value === null) {
                                return '';
                            } else if (angular.isObject(value) || angular.isArray(value)) {
                                throw new Error('ui-codemirror cannot use an object or an array as a model');
                            }
                            return value;
                        });
// Override the ngModelController $render method, which is what gets called when the model is updated.
// This takes care of the synchronizing the codeMirror element with the underlying model, in the case that it is changed by something else.
                        ngModel.$render = function () {
//Code mirror expects a string so make sure it gets one
//Although the formatter have already done this, it can be possible that another formatter returns undefined (for example the required directive)
                            var safeViewValue = ngModel.$viewValue || '';
                            codeMirror.setValue(safeViewValue);
                            window.setTimeout(function () {
                                codeMirror.refresh();
                            }, 100);
                        };
// Keep the ngModel in sync with changes from CodeMirror
                        codeMirror.on('change', function (instance) {
                            var newValue = instance.getValue();
                            if (newValue !== ngModel.$viewValue) {
// Changes to the model from a callback need to be wrapped in $apply or angular will not notice them
                                scope.$apply(function () {
                                    ngModel.$setViewValue(newValue);
                                });
                            }
                        });
                    }
// Watch ui-refresh and refresh the directive
                    if (iAttrs.uiRefresh) {
                        scope.$watch(iAttrs.uiRefresh, function (newVal, oldVal) {
// Skip the initial watch firing
                            window.setTimeout(function () {
                                codeMirror.refresh();
                            }, 100);
                            if (newVal !== oldVal) {
                                window.setTimeout(function () {
                                    codeMirror.refresh();
                                }, 100);
                            }
                        });
                    }
// Allow access to the CodeMirror instance through a broadcasted event
// eg: $broadcast('CodeMirror', function(cm){...});
                    scope.$on('CodeMirror', function (event, callback) {
                        if (angular.isFunction(callback)) {
                            callback(codeMirror);
                        } else {
                            throw new Error('the CodeMirror event requires a callback function');
                        }
                    });
// onLoad callback
                    if (angular.isFunction(opts.onLoad)) {
                        opts.onLoad(codeMirror);
                    }
                };
            }
        };
    }])
    .factory('HashFactory', function () {
        return {
            hash: function (input) {
                return CryptoJS.SHA256(input);
            }, hashString: function (input) {
                return this.getHashInBase64(this.hash(input));
            }, getHashInBase64: function (hash) {
                return hash.toString(CryptoJS.enc.base64);
            }, progressiveHash: function (message) {
                var self = this;
                var hash = CryptoJS.algo.SHA256.create();
                hash.update(message);
                return {
                    add: function (newMsg) {
                        hash.update(newMsg);
                    }, getInBase64: function () {
                        hash.finalize();
                        return self.getHashInBase64(hash);
                    }
                }
            }
        }
    })
    .directive('apixioRequester', function () {
        return {
            transclude: true, scope: {
                okClick: "&", cancelClick: "&", header: "@", apixioRequester: '@'
            }, template: '<div id="{{apixioRequester}}" class="modal fade" tabindex="-1" role="dialog">' +
                '<div class="modal-dialog modal-lg">' +
                '<div class="modal-content">' +
                '<div class="modal-header">' +
                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>' +
                '<h4 class="modal-title">{{header}}</h4>' +
                '</div>' +
                '<div class="modal-body" ng-transclude></div>' +
                '<div class="modal-footer">' +
                '<button type="button" class="btn btn-default" ng-click="cancelClick({event:$event})" data-dismiss="modal">Cancel</button>' +
                '<button type="button" class="btn btn-primary okbtn" ng-click="okClick({event:$event})" ' +
                'data-dismiss="modal">OK</button>' +
                '</div></div></div></div>'
        };
    })
    .directive('dragSource', function () {
        return function (scope, element, attrs) {
            var key = attrs.dragKey || 'moveElement';
            var el = element[0];
            el.draggable = true;
            el.addEventListener('dragstart', function (e) {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData(key, attrs.dragSource);
                return false;
            }, false);
        }
    })
    .directive('dragRearrange', function () {
        return {
            scope: {
                dragRearrange: '=', dragBase: '&', dragInsert: '&'
            }, link: function (scope, element, attrs) {
                var key = attrs.dragKey || 'moveElement';
                var el = element[0];

                function rearrangeList(src, target) {
                    return scope.dragRearrange.splice(target, 0
                        , scope.dragRearrange.splice(src, 1)[0]);
                }

                el.addEventListener('dragover', function (e) {
                    e.dataTransfer.dropEffect = 'move';
                    if (e.preventDefault) e.preventDefault();
                    return false;
                }, false);
                el.addEventListener('drop', function (e) {
                    if (e.stopPropagation) e.stopPropagation();
                    scope.$apply(function (scope) {
                        if (attrs.dragBase)
                            if (scope.dragBase({src: e.dataTransfer.getData(key), target: attrs.dragSource, list: scope.dragRearrange}))
                                return;
                        return rearrangeList(parseInt(e.dataTransfer.getData(key)), parseInt(attrs.dragSource));
                    });
                });
            }
        };
    })
    .directive('aboutPage',function(){
        return{
            template:'<div class="backdrop" ng-show="aboutPage">' +
                '<div class="foredrop">' +
                '<h4>{{appName}}, <small>{{buildString}}</small></h4>'+
                '<a href="javascript:void(0)" ng-click="aboutPage=false">Close</a>'+
            '</div>'
            ,scope:{
                aboutPage:'='
                ,appName:'@'
                ,buildString:'@'
            }
        }
    })
    .directive('safeRemove', function ($timeout) {
        return {
            transclude: true, scope: {
                safeRemove: '=', remove: '&'
            }, template: '<span ng-class="(safeRemove.toBeRemoved)?\'glyphicon-remove-circle\' :' +
                '\'glyphicon-remove\'" ng-click="safelyRemove(safeRemove,$event)"' +
                'class="glyphicon btn btn-danger">' +
                '{{safeRemove.toBeRemoved?" Sure?":""}}</span>' +
                '<span ng-transclude></span>', controller: function ($scope) {
                $scope.safelyRemove = function (obj, ev) {
                    if (!obj.toBeRemoved)
                        obj.toBeRemoved = $timeout(function () {
                            obj.toBeRemoved = false;
                        }, 3000);
                    else {
                        $timeout.cancel(obj.toBeRemoved);
                        obj.toBeRemoved = false;
                        $scope.remove({obj: obj});
                    }
                    ev.stopPropagation();
                    ev.preventDefault();
                }
            }
        }
    }).factory('CubeService',function(){
        function Cube(model,keys){
            this.model=model;
            this.keys=keys;
        }
        Cube.prototype={
            get cube(){
                return this._cube;
            }
            ,get model(){
                return this._model;
            }
            ,set model(v){
                this._model=this._makeArray(v);
                this._resetCube();
            }
            ,get keys(){
                return this._keys;
            }
            ,set keys(v){
                this._keys=this._makeArray(v);
                this._resetCube();
            }
            ,_resetCube:function(){
                this._dims={};
                this._cube=this._model;
                if(this._model)
                    if(this._keys)
                        this.makeCube();
            }
            ,_makeArray:function(v){
                if(!v) return null;
                if(!_.isArray(v)) v=[v];
                return v;
            }
            ,makeCube:function(){
                this._makeDims();
                this._cube=this._aggregate(this._model,this._keys,0);
            }
            ,_makeDims:function(){
                this._dims={};
                _.each(this._keys,function(d){
                    this._dims[d]=true;
                },this);
            }
            ,_addDimToChild:function(dimNames,dimValues){
                var dim={};
                _.each(dimNames,function(dimName,idx){
                    dim[dimName]=dimValues[idx];
                });
                return dim;
            }
            ,_aggregate:function(model,keys,i,values){
                if(!values) values=[];
                var key=keys[i];
                var result={dim: this._addDimToChild(keys.slice(0,i),values)
                    ,facts:[]
                    ,children:{}};
                if(keys.length>i)
                    _.each(_.groupBy(model,key),function(m,k){
                        result.facts=result.facts.concat(m);
                        result.children[k]=this._aggregate(m,keys,i+1,values.concat(k));
                    },this);
                else
                    return {
                        dim:result.dim
                        ,facts: this._removeDims(model)
                    };
                return result;
            }
            ,_removeDims:function (model){
                return _.map(model,function(m){
                    var result={};
                    _.each(m,function(v,k){
                        if(!this._dims[k])
                            result[k]=v;
                    },this);
                    return result;
                },this);
            }
        };
        return{
            create:function(model,keys){
                return new Cube(model,keys);
            }
        }
    })
;


window.apixioXMLAutoComplete = {
    completeAfter: function (cm, pred) {
        if (!this.origXmlHint)
            this.registerHint()
        var cur = cm.getCursor();
        if (!pred || pred()) setTimeout(function () {
            if (!cm.state.completionActive)
                cm.showHint({completeSingle: false});
        }, 100);
        return CodeMirror.Pass;
    }, completeIfAfterLt: function (cm) {
        return this.completeAfter(cm, function () {
            var cur = cm.getCursor();
            return cm.getRange(CodeMirror.Pos(cur.line, cur.ch - 1), cur) == "<";
        });
    }, completeIfInTag: function (cm) {
        var self = this;
        return this.completeAfter(cm, function () {
            var tok = cm.getTokenAt(cm.getCursor());
            if (tok.type == "string" && (!/['"]/.test(tok.string.charAt(tok.string.length - 1)) || tok.string.length == 1)) return false;
            return self.getTagName(cm);
        });
    }, registerHint: function () {
        var self = this;
        this.origXmlHint = CodeMirror.hint.xml;
        CodeMirror.hint.xml = function (cm, info) {
            return self.xmlHint(cm, info);
        }
    }, getTagName: function (cm) {
        return CodeMirror.innerMode(cm.getMode(), cm.getTokenAt(cm.getCursor()).state).state.tagName;
    }, xmlHint: function (cm, info) {
        var tag = this.getTagName(cm);
        var orig = this.origXmlHint(cm, info);
        if (tag)
            if (info.specialSchema[tag])
                return this[info.specialSchema[tag]](cm, info, orig);
        return orig;
    }, removeFromList: function (target, ref) {
        return target.filter(function (t) {
            var ret = true;
            ref.forEach(function (r) {
                if (t == r)
                    ret = false;
            })
            return ret;
        })
    }
};
_.findIndex = function (obj, predicate, context) {
    var result;
    _.any(obj, function (value, index, list) {
        if (!predicate.call(context, value, index, list)) return false;
        result = index;
        return true;
    });
    return result;
};