/**
 * Created by rezaalemy on 14-11-08.
 */
var session=require('express-session');
var flash=require('connect-flash');
var config=require('../config');
var _=require('underscore');
var model=require('../model/model');
var passport=require('passport')
    , GoogleStrategy = require('passport-google-oauth').OAuth2Strategy;
var GOOGLE_CLIENT_ID = "325512600586-ru5918c0bmp6h1dg3hetbko28d9ak3rr.apps.googleusercontent.com";
var GOOGLE_CLIENT_SECRET = "iEpxnhrtYu2Dxr2F_VL0Etyc";

passport.serializeUser(function(user, done) {
    done(null, user);
});
passport.deserializeUser(function(obj, done) {
    done(null, obj);
});

function getValidApixioEmail(profile){
    var email=_.find(profile.emails,function(email){
        return /@apixio.com$/.test(email.value);
    });
    return (email)? email.value:null;
}
function getRole(email){
    return model.getAdminUser().then(function(data){
        if (_.find(data,function(admin){
                return admin.email==email;
            })) return 'admin';
        return 'guest';
    });
}
var activeSessions={};
passport.use(new GoogleStrategy({
        clientID: GOOGLE_CLIENT_ID,
        clientSecret: GOOGLE_CLIENT_SECRET,
        callbackURL: config.appBase()+"/oauth2callback"
    },
    function(accessToken, refreshToken, profile, done) {
        process.nextTick(function () {
            var apixioEmail=getValidApixioEmail(profile);
            if(!apixioEmail)
                return done(null,null,"Not an Apixio email");
            activeSessions[profile.id]={born:new Date().getTime()};
            getRole(apixioEmail).then(function(role){
                activeSessions[profile.id].role=role;
                return done(null, profile);
            },function(err){
                return done(null,null,err);
            });
        });
    }
));

var md={};
md.initialize=function(app){
    app.use(session({secret:'iLoveWorkingForApixioSpeciallyAfterWhiskeyBottlesPopUp',
        resave: true,
        saveUninitialized: true,
        cookie:{maxAge:6000000}}));
    app.use(passport.initialize());
    app.use(passport.session());
    app.use(flash());
    app.get('/auth/google',
        passport.authenticate('google', { scope: ['https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email'] }),
        function(){});
    app.get('/oauth2callback',
        passport.authenticate('google', { failureRedirect: '/badlogin' }),
        function(req, res) {
            res.redirect('/')
        });
    app.get('/logout', function(req, res){
        req.logout();
        res.redirect('/goodbye');
    });
};
function proceed(user,next){
    var profile=activeSessions[user.id];
    profile.born=new Date().getTime();
    user.profile=profile;
    return next();
}
function makeEveryoneAdmin(req){
    //function to create the first administrator
    console.log("user",req.user);
    if(req.user)
        if(activeSessions[req.user.id])
            activeSessions[req.user.id].role='admin';
}
function isRequestedWithAjax(req){
    if(req.headers['x-requested-with'])
        if(req.headers['x-requested-with']=='XMLHttpRequest')
            return true;
    return false;
}
md.ensureAuthentication=function(req,res,next){
    //makeEveryoneAdmin(req); //uncomment for the first admin, then re-comment
    if(req.isAuthenticated())
        if(activeSessions[req.user.id])
            if(new Date().getTime()-activeSessions[req.user.id].born < config.maxInactivity)
                return proceed(req.user,next);
    if(!isRequestedWithAjax(req))
        return res.redirect('/login');
    var err=new Error("Unauthorized access, please log in");
    err.status=401;
    next(err);
};
module.exports=md;
