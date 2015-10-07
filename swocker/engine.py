from TwitterAPI import TwitterAPI
from alchemyapi import AlchemyAPI
from yahoo_finance import Share
import json
import requests
import secrets
import random
import IPython
import urllib
import datetime

global concepts
concepts = []

"""
Returns a list of tweets from Twitter that contains the parameter query
"""
def twit_search(query):
    for twitter_cred in get_random_twitter_credentials():
        api = TwitterAPI(twitter_cred["CONSUMER_KEY"], twitter_cred["CONSUMER_SECRET"],
                        twitter_cred["ACCESS_TOKEN"], twitter_cred["ACCESS_SECRET"])
        request = api.request('search/tweets', {'q':query, 'lang': 'en','count': '100'})
        tweet_texts = []
        tweet_strict_texts = []

        # If keys were over used, move on
        if request.status_code == 403:
            continue

        # Append all tweets to array and return
        for tweet in request.json()['statuses']:
            if tweet['text'] not in tweet_strict_texts:
                format_date = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d')
                tweet_texts.append({
                    'date': format_date,
                    'text': tweet['text']
                })
                tweet_strict_texts.append(tweet['text'])
        return tweet_texts, tweet_strict_texts
    return None, None

"""
Returns json of sentiments for dates
"""
def get_sentiments(tweets):
    sentiment_tweets = []
    for tweet in tweets:
        if relevant_tweet(tweet['text']):
            value = get_sentiment(tweet['text'])
            if value != None:
                sentiment_tweets.append({
                    'date': tweet['date'],
                    'text': tweet['text'],
                    'sentiment': value
                })
    return json.dumps(sentiment_tweets)

"""
Determine if a tweet is relevant to the company
"""
def relevant_tweet(tweet):
    for x in concepts:
        if x.lower() in tweet.lower():
            return True
    return False

"""
Get and store concepts for a company
"""
def store_concepts(tweets):
    # Convert string array to string
    all_tweets_as_string = ' '.join(tweets)
    alchemyapi = AlchemyAPI()
    alchemyapi.apikey = get_random_alchemy_credentials()
    response = alchemyapi.concepts('text', all_tweets_as_string)
    if response['status'] == 'OK':
        for concept in response['concepts']:
            concepts.append(concept['text'])

"""
Return a sentiment for a string of text
http://www.alchemyapi.com/api/keyword/textc.html
"""
def get_sentiment(text):
    alchemyapi = AlchemyAPI()
    alchemyapi.apikey = get_random_alchemy_credentials()
    response = alchemyapi.keywords('text', text, {'sentiment': 1})
    relevances = []
    if 'keywords' not in response or len(response['keywords']) == 0:
        return None
    for keyword in response["keywords"]:
        for company_word in concepts:
            if company_word.lower() in text.lower() and 'sentiment' in keyword:
                if 'score' in keyword['sentiment']:
                    relevances.append(float(keyword['sentiment']['score']))
                elif keyword['sentiment']['type'] == 'neutral':
                    relevances.append(0.5)
    if not relevances:
        return 0.5
    else:
        return float("{0:.2f}".format(sum(relevances)/len(relevances)))

"""
Returns a randomly shuffled twitter credentials array
Prevents overusing of single pair of keys
"""
def get_random_twitter_credentials():
    twitter_creds = secrets.TWITTER_CODES
    random.shuffle(twitter_creds)
    return twitter_creds

"""
Returns an array of random Alchemy access token
"""
def get_random_alchemy_credentials():
    alchemy_creds = secrets.ALCHEMY_CODES
    random.shuffle(alchemy_creds)
    return alchemy_creds

"""
Returns JSON information regarding the history of a stock
"""
def get_share_history(symbol, startDate, endDate):
    share = Share(symbol)
    history = share.get_historical(startDate, endDate)
    return json.dumps(history)

def get_share_price(symbol):
    share = Share(symbol)
    return share.get_price()
