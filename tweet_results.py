import pymongo
import simplejson
import bson
from bson import json_util
import json
import sys

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


if keyword[0] is ".":
    keyword = keyword.replace('.', '#')

import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.cfg')
mongo_url = config.get('Mongo', 'db_url')

client = pymongo.MongoClient(mongo_url)
db = client.get_default_database()

collections = db.collection_names()

if keyword not in collections:
	e_no_collection_match = "There is no collection in the database matching " + keyword + "."
	raise Exception(e_no_collection_match)

tweets = db[keyword]

result_data = tweets.find( {} ).sort('startedAtTime', pymongo.DESCENDING).limit(count)

iterator = True

result_dict = {}

inserts = 0

empty_query = True

for result in result_data:
	unicode(result)
	result_dict[inserts] = result
	inserts += 1
	empty_query = False
	
with open('app/js/tweets.json', 'w') as outfile:
	json.dump(result_dict, outfile, default=json_util.default)

if inserts != count:
	if force == True:
		print str(inserts) + ' tweets of the ' + str(count) + " you requested from the " + keyword + ' collection have been placed in app/js/tweets.json file'
	else:
		e_insert_mismatch = 'You requested ' + str(count) + ' but only ' + str(inserts) + ' tweets are available in the ' + keyword + ' collection. Retry with -f to ignore the mismatch.'
		raise Exception(e_insert_mismatch)
else:
	print str(count) + " tweets in the " + keyword + ' collection have been placed in app/js/tweets.json file'