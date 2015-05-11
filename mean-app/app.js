/**
 * Module dependencies.
 */

var express = require('express')
  ,  path = require('path')
  ,  mongoose = require('mongoose')
  ,  bodyParser = require('body-parser')
  ,  http = require('http')
  ,  multer = require('multer');
  
  
var app_root = 'process.env.IP'

var app = express();

app.set('views', app_root + '/views');
express.static(path.join(app_root, '/public'));
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded
app.use(multer());

var Schema = mongoose.Schema; 

var CaliperSchema = new Schema({  
    context: { type: String, required: true, default: 'http://purl.imsglobal.org/ctx/caliper/v1/MessagingEvent' },  
    type: { type: String, required: true },  
    startedAtTime: { type: Date, required: true },
    actor: { type: String, required: true }, 
    verb: { type: String, required: true }, 
    logged: { type: Date, default: Date.now },
    object: {
      type: { type: String, required: true },
      tweet_id: { type: String, required: true },
      tweet_uri: { type: String, required: true },
      subtype: { type: String, required: true },
      to: { type: String, required: false },
      author: {
        author_uri: { type: String, required: false },
        author_name: { type: String, required: false },
        author_alias: { type: String, required: false }
      },
      text: { type: String, required: true },
      sentiment: { 
        type: { type: String, required: false },
        score: { type: String, required: false },
        color: { type: String, required: false }
      },
      parent: { type: String, required: false },
      user_mentions: { type: Array, required: false },
      hashtags: { type: Array, required: false }
    }
});

var CaliperTweet = mongoose.model('CaliperSchema', CaliperSchema); 


app.get('/api', function (req, res) {
  res.send('Ecomm API is running');
});


app.post('/api/products', function (req, res){
  var caliperTweet;
  console.log("POST: ");
  console.log(req.body);

  
  var tweetObj = new CaliperTweet({
    context: req.body.context,  
    type: req.body.type,  
    startedAtTime: Date.parse(req.body.startedAtTime),
    actor: req.body.actor, 
    verb: req.body.verb,
    object: {
      type: req.body.object.type,
      tweet_id: req.body.object.tweet_id,
      tweet_uri: req.body.object.tweet_uri,
      subtype: req.body.object.subtype,
      to: req.body.object.to,
      text: req.body.object.text,
      author: {
        author_uri: req.body.object.author.author_uri,
        author_alias: req.body.object.author.author_alias,
        author_name: req.body.object.author.author_name
      },
      sentiment: {
        type: req.body.object.sentiment.type,
        score: req.body.object.sentiment.score,
        color: req.body.object.sentiment.color
      },
      parent: req.body.object.parent,
      user_mentions: req.body.object.user_mentions,
      hashtags: req.body.object.hashtags
    }
  });
  
  
  tweetObj.save(function (err) {
    if (!err) {
      return console.log("created");
    } else {
      return console.log(err);
    }
  });
  return res.send(tweetObj);
});


console.log("Express server listening on port 3000");
console.log(app_root);
app.listen(process.env.PORT);
