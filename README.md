# Sentiment Analysis with Python, Twitter, AlchemyAPI, MongoDB, and Angular

This app will let you query Twitter using Python, send each tweet returned into a Mongo database, and then using another Python script pull records out of MongoDB to populate a table in the UI.

## Install Steps

#### This instruction sets assumes the following:
+ You have installed [MongoDB](http://mongodb.org)
+ You have obtained the correct application authentication keys from [Twitter](https://apps.twitter.com/)
+ You have [Python](https://www.python.org/downloads/) installed
+ You have registered for an [API key](http://www.alchemyapi.com/api/register.html) from Alchemy API.

#### Using the Repo:
+ Clone/fork this Repo
+ Run the requirements.txt script with pip to install the python dependencies

``` python
pip install -r requirements.txt
```

##### Setting Config Variables:
+ Open config.py and change the variables to your values
+ Run the script in your terminal to produce the config.cfg file

``` python
python config.py
```

##### Collecting Tweets

+ Run the tweet_collector.py script and pass your search term and result limit as an argument. If your search term includes a hashtag, substitute the # with .

    To search for 30 #mheducation tweets:

``` python
python tweet_collector.py .mheducation 30
```

+ If no errors appear in the terminal, check your Mongo database and collection to make sure the tweets are there.
++ Note that Python creates a new collection for your search term if a collection did not already exist with that as a name

##### Retrieving Tweets
+ Run the tweet_results.py script, passing the number of tweets you'd like to have returned and the collection to search as arguments (the same as the search term you used to collect the tweets).

    To retrieve the latest 10 tweets from your search for #mheducation:

``` python
python tweet_results.py .mheducation 10 
```

+ This script places a JSON file in /app/js/ which the UI will use.

##### Starting the app
+ Start a web server using Python (or the method of your choice) whose root is the /app folder

``` python
cd app
python -m SimpleHTTPServer
```

+ In your browser open [localhost:8000](http://localhost:8000)

##### Using the TweetSensor module:
+ Import the TweetSensor module
+ It Comes with two functions
++ collect_tweets(keyword, count, force=False)
++ get_results(keyword, count, force=False)