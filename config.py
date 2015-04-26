import ConfigParser

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
config.add_section('Alchemy')
config.set('Alchemy', 'api_key', <YOUR_ALCHEMY_API_KEY>)

config.add_section('Twitter')
config.set('Twitter', 'consumer_key', <TWITTER_APP_CONSUMER_KEY>)
config.set('Twitter', 'consumer_secret', <TWITTER_APP_CONSUMER_SECRET>)
config.set('Twitter', 'access_token', <TWITTER_APP_ACCESS_TOKEN>)
config.set('Twitter', 'access_token_secret', <TWITTER_APP_ACCESS_TOKEN_SECRET>)

config.add_section('Mongo')
config.set('Mongo', 'db_url', <MONGODB_URI>)

# Writing our configuration file to 'example.cfg'
with open('config.cfg', 'wb') as configfile:
    config.write(configfile)