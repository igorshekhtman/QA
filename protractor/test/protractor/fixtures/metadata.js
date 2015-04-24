/**
 * Created by rezaalemy on 15-04-15.
 */

var _ = require("lodash"),
    mock = require("../mock-helper"),
    moment = require("moment");

var to = {
    numString: function (value) {
        if (parseFloat(value).toString() == "NaN")
            return value;
        value = Math.round(parseFloat(value) * 100).toString();
        if (value.length === 1)
            value = "00" + value;
        if (value.length === 2)
            value = "0" + value;
        return value.replace(/(..)$/, ".$1")
            .split("").reverse().join("")
            .replace(/(\d{3})/g, "$1,")
            .replace(/,$/, "")
            .split("").reverse().join("")
            .replace(/^[.]/, "0.");
    },
    number: function (value, fraction) {
        return fraction !== 0 ?
            this.numString(value) :
            this.numString(value).replace(/[.]\d\d$/, "");
    },
    dollar: function (value, fraction) {
        if (!value)
            return null;
        return "$" + this.number(value, fraction);
    },
    date: function (value, format) {
        if (!format)
            format = "MM/DD/YYYY hh:mm:ss A";
        else if (typeof format !== "string")
            format = "MM/DD/YYYY";
        return moment(value).format(format);
    },
    rate: function (value, fraction) {
        return this.number(value, fraction) + " /hr"
    },
    ratio: function (value, fraction) {
        return this.number(value * 100, fraction) + "%";
    }
};

var restCallSpy = function (caller, spy, injections) {
    var q = injections.$q,
        options = caller[0],
        canceller = caller.length > 1 ? caller[1] : q.defer(),
        data = JSON.parse(this.restCall.mockData),
        result = "";
    var defer = q.defer();
    defer.canceller = canceller;
    if (options.url.indexOf("/cloud/project/") == 0)
        if (options.url.indexOf("/coder") > -1)
            if (options.params)
                result = "coder_sliced";
            else
                result = "project_coder";
        else if (options.params)
            result = "project_sliced";
        else if (options.url.length > "/cloud/project/".length)
            result = "project";
        else
            result = "projects";
    else if (options.url.indexOf("/cloud/coders") == 0)
        result = "coders";
    else if (options.url.indexOf("/services/project") == 0)
        result = "reference";
    console.info("Intercepted restCall ", options.url, result);
    defer.resolve(data[result]);
    return defer.promise;
}.toString();

var meta = {
    restCallSpy: restCallSpy,
    to: to,
    mockRestCall: function (mockData) {
        var self = this;
        return mock.mockServiceFunction("modelServer", "restCall", self.restCallSpy, ["$q"]).then(function (result) {
            if (result !== "Success")
                throw result;
            return mock.injectData("modelServer", "restCall", "end", JSON.stringify(mockData)).then(function (result) {
                if (result !== "Success")
                    throw result;
                return self.forceReload();
            });
        });
    },
    forceReload: function () {
        return browser.executeAsyncScript(function (cb) {
            var scope = angular.element(document.querySelector(".ng-scope")).scope();
            if (!scope)
                return cb("Failed to get scope");
            scope.$emit("forceReload");
            scope.$emit("showAlert", false);
            cb("Success");
        });
    },
    getRecentProject: function (projects) {
        return _.max(projects, function (project) {
            if (project.metrics)
                if (project.metrics.coderLastDate)
                    return project.metrics.coderLastDate;
            return -1;
        });
    },
    CWIAnnotated: {
        missing: function () {
            return "No CWIs Annotated";
        },
        show: function (p) {
            if (p.metrics.CWIAnnotated)
                return to.number(p.metrics.CWIAnnotated, 0);
            return this.missing();
        }
    },
    oppsAccepted: {
        missing: function () {
            return "No Opportunities Accepted";
        },
        show: function (p) {
            if (p.metrics.oppsAccepted)
                return to.number(p.metrics.oppsAccepted, 0);
            return this.missing();
        }
    },
    submittableCodes: {
        missing: function () {
            return "0";
//            return "No Submittable Codes";
        },
        show: function (p) {
            if (p.metrics.submittableCodes)
                return to.number(p.metrics.submittableCodes, 0)
                    || this.missing();
            return this.missing();
        }
    },
    coderHours: {
        missing: function () {
            return "No Coder Hours";
        },
        show: function (p) {
            if (p.metrics.coderHours)
                return to.number(p.metrics.coderHours) + " Hrs";
            return this.missing();
        }
    },
    coderCost: {
        missing: function () {
            return "No Coder Cost";
        },
        show: function (p) {
            if (p.metrics.coderCost)
                return to.dollar(p.metrics.coderCost);
            return this.missing();
        }
    },
    coderLastDate: {
        missing: function () {
            return "Latest activity recorded: No Coder Last Activity";
        },
        show: function (p) {
            if (p.metrics.coderLastDate)
                return "Latest activity recorded: " + to.date(p.metrics.coderLastDate);
            return this.missing();
        }
    }
};

module.exports = meta;