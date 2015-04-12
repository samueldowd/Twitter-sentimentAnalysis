from TwitterSearch import *
import pymongo
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
from alchemyapi import AlchemyAPI
import sys

arg_keyword = str(sys.argv[1])

client = pymongo.MongoClient('localhost', 27017)

alchemyapi = AlchemyAPI()

db = client.twitterAnalysis

if arg_keyword[0] is ".":
    arg_keyword = arg_keyword.replace('.', '#')

tweets = db[arg_keyword]

db_count = tweets.count()

if db_count is not 0:
    latest_id = tweets.find( {}, { 'object.tweet_id':1 } ).sort("startedAtTime").limit(1)
    latest_id_str = latest_id[db_count-1]['object']['tweet_id']
    latest_id_int = int(latest_id_str)
    print 'Count of documents in Mongo is not 0. It is ' + str(db_count) + '. Mongo is now identifying the latest tweet ID to append as a parameter to the API call.'
else:
    print 'The Mongo collection ' + arg_keyword + ' is empty. The script will now collect all tweets.'
# create a TwitterSearchOrder object
tso = TwitterSearchOrder() 

    # let's define all words we would like to have a look for
tso.set_keywords([arg_keyword])

    # we want to see English tweets only
tso.set_language('en') 

    # and don't give us all those entity information
tso.set_include_entities(True)

if db_count is not 0:
    tso.set_since_id(latest_id_int)
    print 'Since the document count in ' + arg_keyword + ' is above 0, the since_id uses the parameter of the latest tweet so that only new tweets are collected.'
else:
	print 'No documents exist in the ' + arg_keyword + ' collection right now so the since_id parameter will be empty and all tweets will be collected.'

# it's time to create a TwitterSearch object with our secret tokens
ts = TwitterSearch(
    consumer_key = '<YOUR_TWITTER_CONSUMER_KEY_HERE>',
    consumer_secret = '<YOUR_TWITTER_CONSUMER_SECRET_HERE>',
    access_token = '<YOUR_TWITTER_ACCESS_TOKEN_HERE>',
    access_token_secret = '<YOUR_TWITTER_ACCESS_TOKEN_SECRET_HERE>'
 )

# caliper_tweet = {
#   "@context": "http://purl.imsglobal.org/ctx/caliper/v1/MessagingEvent",
#   "@type": "MessagingEvent",
#   "startedAtTime": "{{ created_at }}",
#   ## Can be used to query Twitter API for user information
#   "actor": "uri:twitter/user/{{ user['id_str'] }}",
#   "verb": "tweetSent",
#   "object": {
#     "@type": "tweet",
#     "@id": "uri:twitter/tweet/{{ id_str}}",
#     "subtype": "tweet",
#     ## "to" should be calculated by checking in_reply_to_user_id_str is null. If it's not null, then it should be concatenated to "uri:twitter/user/" and stored in "object"['to']
#     "to": "uri:twitter/user/{{ in_reply_to_user_id_str }}",
#     "author": "uri:twitter/user/{{ user['id_str'] }}",
#     "text": "{{ text }}",
#     "parent": "uri:twitter/tweet/{{ in_reply_to_user_id_str }}",
#     ## "mentions" is an array of the caliper IDs from the user_mentions objects array
#     "mentions": ["uri:twitter/user/{{ entities[user_mentions]['id_str'] }}", "..." ],
#     ## "hashtags" is an array of the hashtag texts included in the tweet entities
#     "hashtags": ["{{ entities[hashtags][text] }}", " "]
#   }
# }

# Open the variables
db_inserts = 0
caliper_tweet_object = {}
twitter_id_list = []
twitter_search = ts.search_tweets_iterable(tso)
tweet_sentiment = ''

# this is where the fun actually starts :)
for tweet in twitter_search:
    mentions_list = []
    hashtags_list = []
    tweet_id = ""
    # Create the caliper_tweet object
    caliper_tweet = {
  "context": "http://purl.imsglobal.org/ctx/caliper/v1/MessagingEvent",
  "type": "MessagingEvent",
  "startedAtTime": "",
  ## Can be used to query Twitter API for user information
  "actor": "",
  "verb": "tweetSent",
  "object": {
    "type": "MessagingEvent",
    "tweet_id": "",
    "tweet_uri": "",
    "subtype": "tweet",
    ## "to" should be calculated by checking in_reply_to_user_id_str is null. If it's not null, then it should be concatenated to "uri:twitter/user/" and stored in "object"['to']
    "to": "",
    "author": {
        "author_uri": "",
        "author_alias": "",
        "author_name": "",
        },
    "text": "",
    "sentiment": {
        "type": "",
        "score": "",
        "color": ""
    },
    "parent": "",
    ## "mentions" is an array of the caliper IDs from the user_mentions objects array
    "user_mentions": [],
    ## "hashtags" is an array of the hashtag texts included in the tweet entities
    "hashtags": []
  }
}

    ## AlchemyAPI Sentiment Analysis
    response = alchemyapi.sentiment('text', tweet_text)
    if 'type' in response['docSentiment'] and not None:
        if 'score' in response['docSentiment']:
            tweet_sentiment_score = response['docSentiment']['score']
            tweet_sentiment_score = float(tweet_sentiment_score)
            tweet_sentiment_score = round(tweet_sentiment_score, 2)
        else:
            tweet_sentiment_score = 0
        tweet_sentiment_type = response['docSentiment']['type']
        tweet_sentiment_score_a = abs(tweet_sentiment_score)
        if (tweet_sentiment_score) > 0:
            tweet_sentiment_color = "rgba(0,255,0," + str(tweet_sentiment_score_a) + ")"
        else: 
            tweet_sentiment_color = "rgba(255,0,0," + str(tweet_sentiment_score_a) + ")"
    else:
        print "Error"        

    # Set the re-usable variables
    user_id = tweet['user']['id_str']
    tweet_text = tweet['text']
    tweet_id = tweet['id_str']

    ds = tweet['created_at']
    tweet_date = parse(ds)
    caliper_tweet['startedAtTime'] = tweet_date
    caliper_tweet['actor'] = 'student:' + tweet['user']['screen_name']
    caliper_tweet['object']['tweet_uri'] = 'https://twitter.com/' + tweet['user']['screen_name'] + '/status/' + tweet_id
    caliper_tweet['object']['tweet_id'] = tweet['id_str']
    if tweet['in_reply_to_user_id_str'] is None:
        caliper_tweet['object']['to'] = 'NoReply'
        caliper_tweet['object']['parent'] = 'NoReply'
    else:
        caliper_tweet['object']['to'] = 'https://twitter.com/intent/user?user_id=' + tweet['in_reply_to_user_id_str']
        if tweet['in_reply_to_status_id_str'] is None:
            caliper_tweet['object']['parent'] = 'None'
        else:    
            caliper_tweet['object']['parent'] = 'https://twitter.com/' + tweet['user']['screen_name'] + '/status/' + tweet['in_reply_to_status_id_str']
    caliper_tweet['object']['author']['author_uri'] = 'https://twitter.com/intent/user?user_id=' + tweet['user']['id_str']
    caliper_tweet['object']['author']['author_alias'] = tweet['user']['screen_name']
    caliper_tweet['object']['author']['author_name'] = tweet['user']['name']
    caliper_tweet['object']['text'] = unicode(tweet['text'])
    if tweet_sentiment is not 'None':
        caliper_tweet['object']['sentiment']['type'] = tweet_sentiment_type
        caliper_tweet['object']['sentiment']['score'] = tweet_sentiment_score
        caliper_tweet['object']['sentiment']['color'] = tweet_sentiment_color

    for x in list(tweet['entities']['hashtags']):
        hashtag = x['text']
        hashtags_list.append(hashtag)
    for x in list(tweet['entities']['user_mentions']):
        mention = x['id_str']
        mentions_list.append(mention)
    caliper_tweet['object']['user_mentions'] = mentions_list
    caliper_tweet['object']['hashtags'] = hashtags_list
 
    tweets.insert(caliper_tweet)
    
    db_inserts = db_inserts + 1

    print str(db_inserts) + " were made."

print 'deadbeef'
print str(db_inserts) + " inserts made."
