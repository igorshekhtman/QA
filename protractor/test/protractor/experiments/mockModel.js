/**
 * Created by rezaalemy on 15-04-02.
 */

var modelServer=function($q){
    var projects=[{"projectId":"CP_f79c8f1a-4014-4f0d-95cd-484646c5b20a","projectName":"300 Patient Test Project","customerId":"372","customerName":"MMG","budget":20000.0,"rafTarget":20.0,"rafPoint":0.33,"metrics":{"oppsAccepted":23.0,"CWISkipped":260.0,"oppsCreated":133.0,"coderHours":5.124050833333336,"oppsRejected":14.0,"coderStartDate":1.427326179075E12,"overturns":0.0,"oppsFlagged":4.0,"oppsAnnotated":67.0,"coderCost":241.48801549999996,"QWIAnnotated":22.0,"SubmitableCodes":0.0,"CWIAccepted":124.0,"QWISkipped":22.0,"CWIAnnotated":471.0,"CWIRejected":87.0,"CWIRemaining":0.0}},{"projectId":"CP_d616cbdf-8643-4664-ae88-75ce441881b3","projectName":"UAT MMG","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":0.0,"rafPoint":0.55,"metrics":{"oppsAccepted":0.0,"CWISkipped":0.0,"oppsCreated":308.0,"coderHours":0.09650638888888889,"oppsRejected":0.0,"coderStartDate":1.427935307191E12,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"coderCost":4.603354750000001,"QWIAnnotated":0.0,"SubmitableCodes":0.0,"CWIAccepted":2.0,"QWISkipped":0.0,"CWIAnnotated":9.0,"CWIRejected":7.0,"CWIRemaining":0.0}},{"projectId":"CP_3600860c-9371-489c-ba16-26fee2986b21","projectName":"test_22","customerId":"406","customerName":"Wellpoint","budget":1.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_553bd2e4-686a-476c-9bb3-a55cae4da3b6","projectName":"Test on Sanity","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.1,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c0810d74-bae7-466e-a200-51175a38ddd9","projectName":"Hometown Health 10k","customerId":"407","customerName":"Hometown Health","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":10.0,"CWISkipped":81.0,"oppsCreated":28338.0,"coderHours":2.1414355555555544,"oppsRejected":12.0,"coderStartDate":1.427832189563E12,"overturns":0.0,"oppsFlagged":2.0,"oppsAnnotated":63.0,"coderCost":100.94792822222225,"QWIAnnotated":7.0,"SubmitableCodes":0.0,"CWIAccepted":12.0,"QWISkipped":7.0,"CWIAnnotated":106.0,"CWIRejected":13.0,"CWIRemaining":0.0}},{"projectId":"CP_8b5e8619-4135-4ede-9323-ff9eb79162f1","projectName":"test_24","customerId":"382","customerName":"Sanity Test","budget":10.0,"rafTarget":10.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_1b4a1b9e-c729-4694-9465-276f93ee5eb6","projectName":"New Test Project","customerId":"382","customerName":"Sanity Test","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c36887d1-c9e3-4e2c-821a-29d310fa1628","projectName":"MMG 5K Project","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":0.0,"oppsCreated":6060.0,"oppsRejected":0.0,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"SubmitableCodes":0.0,"CWIRemaining":0.0}},{"projectId":"CP_66d8c94e-0312-4524-84c5-05491d1275c9","projectName":"Another Test Project","customerId":"372","customerName":"MMG","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"","projectName":"UNKNOWN","customerId":"0","customerName":"UNKNOWN","budget":0.0,"rafTarget":0.0,"rafPoint":0.0,"metrics":{"oppsAccepted":4.0,"CWISkipped":67.0,"oppsCreated":63.0,"coderHours":2.6124208333333336,"oppsRejected":12.0,"coderStartDate":1.426784739808E12,"overturns":0.0,"oppsFlagged":5.0,"oppsAnnotated":52.0,"coderCost":124.45090094444447,"QWIAnnotated":33.0,"SubmitableCodes":0.0,"CWIAccepted":7.0,"QWISkipped":33.0,"CWIAnnotated":86.0,"CWIRejected":12.0,"CWIRemaining":0.0}},{"projectId":"CP_db4b3dc1-8955-4b04-a794-cf0ac8ef114c","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_804040e3-21dd-4206-bb6f-43789f10b05a","projectName":"test_25","customerId":"395","customerName":"Alex","budget":12.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_ce5b1fff-433f-406d-87c2-6eeeae91b3df","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}}];
    var services=[{"projectId":"CP_f79c8f1a-4014-4f0d-95cd-484646c5b20a","projectName":"300 Patient Test Project","customerId":"372","customerName":"MMG","budget":20000.0,"rafTarget":20.0,"rafPoint":0.33,"metrics":{"oppsAccepted":23.0,"CWISkipped":260.0,"oppsCreated":133.0,"coderHours":5.124050833333336,"oppsRejected":14.0,"coderStartDate":1.427326179075E12,"overturns":0.0,"oppsFlagged":4.0,"oppsAnnotated":67.0,"coderCost":241.48801549999996,"QWIAnnotated":22.0,"SubmitableCodes":0.0,"CWIAccepted":124.0,"QWISkipped":22.0,"CWIAnnotated":471.0,"CWIRejected":87.0,"CWIRemaining":0.0}},{"projectId":"CP_d616cbdf-8643-4664-ae88-75ce441881b3","projectName":"UAT MMG","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":0.0,"rafPoint":0.55,"metrics":{"oppsAccepted":0.0,"CWISkipped":0.0,"oppsCreated":308.0,"coderHours":0.09650638888888889,"oppsRejected":0.0,"coderStartDate":1.427935307191E12,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"coderCost":4.603354750000001,"QWIAnnotated":0.0,"SubmitableCodes":0.0,"CWIAccepted":2.0,"QWISkipped":0.0,"CWIAnnotated":9.0,"CWIRejected":7.0,"CWIRemaining":0.0}},{"projectId":"CP_3600860c-9371-489c-ba16-26fee2986b21","projectName":"test_22","customerId":"406","customerName":"Wellpoint","budget":1.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_553bd2e4-686a-476c-9bb3-a55cae4da3b6","projectName":"Test on Sanity","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.1,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c0810d74-bae7-466e-a200-51175a38ddd9","projectName":"Hometown Health 10k","customerId":"407","customerName":"Hometown Health","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":10.0,"CWISkipped":81.0,"oppsCreated":28338.0,"coderHours":2.1414355555555544,"oppsRejected":12.0,"coderStartDate":1.427832189563E12,"overturns":0.0,"oppsFlagged":2.0,"oppsAnnotated":63.0,"coderCost":100.94792822222225,"QWIAnnotated":7.0,"SubmitableCodes":0.0,"CWIAccepted":12.0,"QWISkipped":7.0,"CWIAnnotated":106.0,"CWIRejected":13.0,"CWIRemaining":0.0}},{"projectId":"CP_8b5e8619-4135-4ede-9323-ff9eb79162f1","projectName":"test_24","customerId":"382","customerName":"Sanity Test","budget":10.0,"rafTarget":10.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_1b4a1b9e-c729-4694-9465-276f93ee5eb6","projectName":"New Test Project","customerId":"382","customerName":"Sanity Test","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c36887d1-c9e3-4e2c-821a-29d310fa1628","projectName":"MMG 5K Project","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":0.0,"oppsCreated":6060.0,"oppsRejected":0.0,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"SubmitableCodes":0.0,"CWIRemaining":0.0}},{"projectId":"CP_66d8c94e-0312-4524-84c5-05491d1275c9","projectName":"Another Test Project","customerId":"372","customerName":"MMG","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"","projectName":"UNKNOWN","customerId":"0","customerName":"UNKNOWN","budget":0.0,"rafTarget":0.0,"rafPoint":0.0,"metrics":{"oppsAccepted":4.0,"CWISkipped":67.0,"oppsCreated":63.0,"coderHours":2.6124208333333336,"oppsRejected":12.0,"coderStartDate":1.426784739808E12,"overturns":0.0,"oppsFlagged":5.0,"oppsAnnotated":52.0,"coderCost":124.45090094444447,"QWIAnnotated":33.0,"SubmitableCodes":0.0,"CWIAccepted":7.0,"QWISkipped":33.0,"CWIAnnotated":86.0,"CWIRejected":12.0,"CWIRemaining":0.0}},{"projectId":"CP_db4b3dc1-8955-4b04-a794-cf0ac8ef114c","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_804040e3-21dd-4206-bb6f-43789f10b05a","projectName":"test_25","customerId":"395","customerName":"Alex","budget":12.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_ce5b1fff-433f-406d-87c2-6eeeae91b3df","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}}];
    var coders=[{'coderId': 'bkrebs@apixio.com', 'first': 1427831818261, 'last': 1427832131638, 'projectId': 'CP_f79c8f1a-4014-4f0d-95cd-484646c5b20a'}];
function restCall(data){
        var defer=$q.defer();
        defer.resolve(data);
        return defer.promise;
    }
    return {
        getProjectDetails:function(projectId){
            return restCall(projects[0]);
        },
        getProjects:function(){
            return restCall(projects);
        },
        getActiveCoders:function(){
            return restCall(coders);
        },
        getProjectInfo:function(){
            return restCall(services);
        }
    };
};
//module.exports='["$q",'+modelServer.toString()+']';

var mockData={
    projects:[{"projectId":"CP_f79c8f1a-4014-4f0d-95cd-484646c5b20a","projectName":"300 Patient Test Project","customerId":"372","customerName":"MMG","budget":20000.0,"rafTarget":20.0,"rafPoint":0.33,"metrics":{"oppsAccepted":23.0,"CWISkipped":260.0,"oppsCreated":133.0,"coderHours":5.124050833333336,"oppsRejected":14.0,"coderStartDate":1.427326179075E12,"overturns":0.0,"oppsFlagged":4.0,"oppsAnnotated":67.0,"coderCost":241.48801549999996,"QWIAnnotated":22.0,"SubmitableCodes":0.0,"CWIAccepted":124.0,"QWISkipped":22.0,"CWIAnnotated":471.0,"CWIRejected":87.0,"CWIRemaining":0.0}},{"projectId":"CP_d616cbdf-8643-4664-ae88-75ce441881b3","projectName":"UAT MMG","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":0.0,"rafPoint":0.55,"metrics":{"oppsAccepted":0.0,"CWISkipped":0.0,"oppsCreated":308.0,"coderHours":0.09650638888888889,"oppsRejected":0.0,"coderStartDate":1.427935307191E12,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"coderCost":4.603354750000001,"QWIAnnotated":0.0,"SubmitableCodes":0.0,"CWIAccepted":2.0,"QWISkipped":0.0,"CWIAnnotated":9.0,"CWIRejected":7.0,"CWIRemaining":0.0}},{"projectId":"CP_3600860c-9371-489c-ba16-26fee2986b21","projectName":"test_22","customerId":"406","customerName":"Wellpoint","budget":1.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_553bd2e4-686a-476c-9bb3-a55cae4da3b6","projectName":"Test on Sanity","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.1,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c0810d74-bae7-466e-a200-51175a38ddd9","projectName":"Hometown Health 10k","customerId":"407","customerName":"Hometown Health","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":10.0,"CWISkipped":81.0,"oppsCreated":28338.0,"coderHours":2.1414355555555544,"oppsRejected":12.0,"coderStartDate":1.427832189563E12,"overturns":0.0,"oppsFlagged":2.0,"oppsAnnotated":63.0,"coderCost":100.94792822222225,"QWIAnnotated":7.0,"SubmitableCodes":0.0,"CWIAccepted":12.0,"QWISkipped":7.0,"CWIAnnotated":106.0,"CWIRejected":13.0,"CWIRemaining":0.0}},{"projectId":"CP_8b5e8619-4135-4ede-9323-ff9eb79162f1","projectName":"test_24","customerId":"382","customerName":"Sanity Test","budget":10.0,"rafTarget":10.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_1b4a1b9e-c729-4694-9465-276f93ee5eb6","projectName":"New Test Project","customerId":"382","customerName":"Sanity Test","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c36887d1-c9e3-4e2c-821a-29d310fa1628","projectName":"MMG 5K Project","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":0.0,"oppsCreated":6060.0,"oppsRejected":0.0,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"SubmitableCodes":0.0,"CWIRemaining":0.0}},{"projectId":"CP_66d8c94e-0312-4524-84c5-05491d1275c9","projectName":"Another Test Project","customerId":"372","customerName":"MMG","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"","projectName":"UNKNOWN","customerId":"0","customerName":"UNKNOWN","budget":0.0,"rafTarget":0.0,"rafPoint":0.0,"metrics":{"oppsAccepted":4.0,"CWISkipped":67.0,"oppsCreated":63.0,"coderHours":2.6124208333333336,"oppsRejected":12.0,"coderStartDate":1.426784739808E12,"overturns":0.0,"oppsFlagged":5.0,"oppsAnnotated":52.0,"coderCost":124.45090094444447,"QWIAnnotated":33.0,"SubmitableCodes":0.0,"CWIAccepted":7.0,"QWISkipped":33.0,"CWIAnnotated":86.0,"CWIRejected":12.0,"CWIRemaining":0.0}},{"projectId":"CP_db4b3dc1-8955-4b04-a794-cf0ac8ef114c","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_804040e3-21dd-4206-bb6f-43789f10b05a","projectName":"test_25","customerId":"395","customerName":"Alex","budget":12.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_ce5b1fff-433f-406d-87c2-6eeeae91b3df","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}}]
,services:[{"projectId":"CP_f79c8f1a-4014-4f0d-95cd-484646c5b20a","projectName":"300 Patient Test Project","customerId":"372","customerName":"MMG","budget":20000.0,"rafTarget":20.0,"rafPoint":0.33,"metrics":{"oppsAccepted":23.0,"CWISkipped":260.0,"oppsCreated":133.0,"coderHours":5.124050833333336,"oppsRejected":14.0,"coderStartDate":1.427326179075E12,"overturns":0.0,"oppsFlagged":4.0,"oppsAnnotated":67.0,"coderCost":241.48801549999996,"QWIAnnotated":22.0,"SubmitableCodes":0.0,"CWIAccepted":124.0,"QWISkipped":22.0,"CWIAnnotated":471.0,"CWIRejected":87.0,"CWIRemaining":0.0}},{"projectId":"CP_d616cbdf-8643-4664-ae88-75ce441881b3","projectName":"UAT MMG","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":0.0,"rafPoint":0.55,"metrics":{"oppsAccepted":0.0,"CWISkipped":0.0,"oppsCreated":308.0,"coderHours":0.09650638888888889,"oppsRejected":0.0,"coderStartDate":1.427935307191E12,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"coderCost":4.603354750000001,"QWIAnnotated":0.0,"SubmitableCodes":0.0,"CWIAccepted":2.0,"QWISkipped":0.0,"CWIAnnotated":9.0,"CWIRejected":7.0,"CWIRemaining":0.0}},{"projectId":"CP_3600860c-9371-489c-ba16-26fee2986b21","projectName":"test_22","customerId":"406","customerName":"Wellpoint","budget":1.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_553bd2e4-686a-476c-9bb3-a55cae4da3b6","projectName":"Test on Sanity","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.1,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c0810d74-bae7-466e-a200-51175a38ddd9","projectName":"Hometown Health 10k","customerId":"407","customerName":"Hometown Health","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":10.0,"CWISkipped":81.0,"oppsCreated":28338.0,"coderHours":2.1414355555555544,"oppsRejected":12.0,"coderStartDate":1.427832189563E12,"overturns":0.0,"oppsFlagged":2.0,"oppsAnnotated":63.0,"coderCost":100.94792822222225,"QWIAnnotated":7.0,"SubmitableCodes":0.0,"CWIAccepted":12.0,"QWISkipped":7.0,"CWIAnnotated":106.0,"CWIRejected":13.0,"CWIRemaining":0.0}},{"projectId":"CP_8b5e8619-4135-4ede-9323-ff9eb79162f1","projectName":"test_24","customerId":"382","customerName":"Sanity Test","budget":10.0,"rafTarget":10.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_1b4a1b9e-c729-4694-9465-276f93ee5eb6","projectName":"New Test Project","customerId":"382","customerName":"Sanity Test","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_c36887d1-c9e3-4e2c-821a-29d310fa1628","projectName":"MMG 5K Project","customerId":"372","customerName":"MMG","budget":10000.0,"rafTarget":13.0,"rafPoint":0.33,"metrics":{"oppsAccepted":0.0,"oppsCreated":6060.0,"oppsRejected":0.0,"overturns":0.0,"oppsFlagged":0.0,"oppsAnnotated":0.0,"SubmitableCodes":0.0,"CWIRemaining":0.0}},{"projectId":"CP_66d8c94e-0312-4524-84c5-05491d1275c9","projectName":"Another Test Project","customerId":"372","customerName":"MMG","budget":0.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"","projectName":"UNKNOWN","customerId":"0","customerName":"UNKNOWN","budget":0.0,"rafTarget":0.0,"rafPoint":0.0,"metrics":{"oppsAccepted":4.0,"CWISkipped":67.0,"oppsCreated":63.0,"coderHours":2.6124208333333336,"oppsRejected":12.0,"coderStartDate":1.426784739808E12,"overturns":0.0,"oppsFlagged":5.0,"oppsAnnotated":52.0,"coderCost":124.45090094444447,"QWIAnnotated":33.0,"SubmitableCodes":0.0,"CWIAccepted":7.0,"QWISkipped":33.0,"CWIAnnotated":86.0,"CWIRejected":12.0,"CWIRemaining":0.0}},{"projectId":"CP_db4b3dc1-8955-4b04-a794-cf0ac8ef114c","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_804040e3-21dd-4206-bb6f-43789f10b05a","projectName":"test_25","customerId":"395","customerName":"Alex","budget":12.0,"rafTarget":1.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}},{"projectId":"CP_ce5b1fff-433f-406d-87c2-6eeeae91b3df","projectName":"test_23","customerId":"370","customerName":"Sanity Test Org","budget":1.0,"rafTarget":0.0,"rafPoint":0.33,"metrics":{"CWIRemaining":0.0,"SubmitableCodes":0.0}}]
,coderMap:[{'coderId': 'bkrebs@apixio.com', 'first': 1427831818261, 'last': 1427832131638, 'projectId': 'CP_f79c8f1a-4014-4f0d-95cd-484646c5b20a'}]
};
module.exports=mockData;