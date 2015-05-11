from TwitterSearch import TwitterSearch
from TwitterSearch import TwitterSearchOrder
import pymongo
from dateutil.parser import parse
from alchemyapi import AlchemyAPI
# Read the config file for config variables
import ConfigParser
import sys
import requests
from datetime import datetime
import json


try:
    keyword = sys.argv[1]
    count = int(sys.argv[2])
except IndexError:
	e_too_few_args = "You did not enter enough arguments. Two are required: keyword, and count"
	raise Exception(e_too_few_args)

try:
    if sys.argv[3] == '-f':
        force = True
    else:
        e_invalid_argument = "The only option available is -f. It is used to force the script to continue when the Alchemy API limit is exceeded."
        raise Exception(e_invalid_argument)
except IndexError:
    force = False

config = ConfigParser.RawConfigParser()
config.read('config.cfg')
mongo_url = config.get('Mongo', 'db_url')

# Connect to the Mongo database using MongoClient

client = pymongo.MongoClient(mongo_url)
db = client.get_default_database()
# Access/create the collection based on the command line argument
tweets = db[keyword]

#Generate the alchemyapi variable
alchemyapi = AlchemyAPI()

# To accommodate for hashtags the user can substitute a . for the # in the command line. Lines 30 & 31 return it to a hashtag for the search.
if keyword[0] is ".":
    keyword = keyword.replace('.', '#')

# Lines 33-42 ensure that the query is not doing duplicate work.
# First, it counts to see how many documents exist in the collection
db_count = tweets.count()

# If there are documents in the collection, the collection is queried, tweet objects are sorted by date, and the tweet_id of the most recent tweet is retrieved and later set as the "since_id"
if db_count is not 0:
    latest_id = tweets.find( {}, { 'object.tweet_id':1 } ).sort("startedAtTime").limit(1)
    latest_id_str = latest_id[db_count-1]['object']['tweet_id']
    latest_id_int = int(latest_id_str)
    print 'Count of documents in the ' + keyword + ' collection is not 0. It is ' + str(db_count) + '. Mongo is now identifying the latest tweet ID to append as a parameter to the API call.'
# If ther are no documents in the collection, no queries are done, and the since_id is left out of the API call.    
else:
    print 'The Mongo collection ' + keyword + ' is empty. The script will now collect all tweets.'
    
# create a TwitterSearchOrder object
tso = TwitterSearchOrder() 

# let's define all words we would like to have a look for
tso.set_keywords([keyword])

# Select language
tso.set_language('en') 

# Include Entity information
tso.set_include_entities(True)

if db_count is not 0:
    tso.set_since_id(latest_id_int)
    print 'Since the document count in the ' + keyword + ' collection is above 0, the since_id uses the parameter of the latest tweet so that only new tweets are collected.'
else:
	print 'No documents exist in the ' + keyword + ' collection right now so the since_id parameter will be empty and all tweets will be collected.'

    
# Create a TwitterSearch object with our secret tokens
ts = TwitterSearch(
    consumer_key = config.get('Twitter', 'consumer_key'),
    consumer_secret = config.get('Twitter', 'consumer_secret'),
    access_token = config.get('Twitter', 'access_token'),
    access_token_secret = config.get('Twitter', 'access_token_secret')
 )
 
# Perform the search
twitter_search = ts.search_tweets_iterable(tso)

# Start the insert count variable
db_inserts = 0

# this is where the fun actually starts :)
try:
    for tweet in twitter_search:
        if db_inserts < count:
            mentions_list = []
            hashtags_list = []
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
            
             # Set the re-usable variables
            tweet_text = tweet['text']
            
            ## AlchemyAPI Sentiment Analysis
            tweet_sentiment = ''
            response = alchemyapi.sentiment('text', tweet_text)
            if 'docSentiment' in response.keys():
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
            elif force == True:
                print 'force option set to True. The tweet_sentiment object will be set with API Limit Exceeded values.'
                tweet_sentiment_type = 'API Limit Exceeded'
                tweet_sentiment_score = 0
                tweet_sentiment_color = 'rgba(0,0,0,0)'
            else:
                e_alchemy_api_limit = 'Alchemy API daily limit exceeded. Retry search with -f option to continue'
                raise Exception(e_alchemy_api_limit)
                
        
            ds = tweet['created_at']
            parsed_date = parse(ds)
            tweet_date = str(parsed_date)
            caliper_tweet['startedAtTime'] = tweet_date
            caliper_tweet['actor'] = 'student:' + tweet['user']['screen_name']
            caliper_tweet['object']['tweet_uri'] = 'https://twitter.com/' + tweet['user']['screen_name'] + '/status/' + tweet['id_str']
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
         
            print type(caliper_tweet)
            print caliper_tweet

            tweets.insert(caliper_tweet)
            
            # def set_default(obj):
            #     if isinstance(obj, set):
            #         return list(obj)
            #     raise TypeError
            
            # result = json.dumps(caliper_tweet, default=set_default)
            
            db_inserts = db_inserts + 1
            # tweets_list = list(caliper_tweet)
            # json_tweets = json.dumps(caliper_tweet)
            # print result
            r = requests.post("https://twitter-sentimentanalysis-samueldowd.c9.io/api/products", data=caliper_tweet)
            print r.status_code
            
        else:
            raise StopIteration
except StopIteration:
    print str(db_inserts) + " inserts made in the " + keyword + " collection."