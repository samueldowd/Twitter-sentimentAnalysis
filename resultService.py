import pymongo
import simplejson
import bson
from bson import json_util
import json
import sys

arg_count = int(sys.argv[1])
arg_keyword = sys.argv[2]

if arg_keyword[0] is ".":
    arg_keyword = arg_keyword.replace('.', '#')

client = pymongo.MongoClient('localhost', 27017)

db = client.twitterAnalysis

tweets = db[arg_keyword]

result_data = tweets.find( {} ).sort('startedAtTime', pymongo.DESCENDING).limit(arg_count)

iterator = True

result_dict = {}

key = 1

print result_data.alive

while iterator is True:
	print iterator
	result = result_data.next()
	print result
	unicode(result)
	print type(result)
	result_dict[key] = result
	iterator = result_data.alive
	key += 1	
else:
	print 'done'

with open('app/js/tweets.json', 'w') as outfile:
	json.dump(result_dict, outfile, default=json_util.default)


print result_dict

print 'deadbeef'