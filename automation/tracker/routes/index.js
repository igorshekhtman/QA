var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/login', function(req, res) {
  res.render('index', { title: 'Welcome to Apixio QA Framework' });
});

router.get('/badlogin',function(req,res){
  res.render('index', { title: 'Bad Login. Please use Apixio email account for log in' });
});
router.get('/goodbye',function(req,res){
  res.render('index', { title: 'End of session. Please login again to continue' });
});
module.exports = router;
