from swocker import engine
from datetime import datetime, timedelta
import json
import IPython

"""
Refresh tweets if and only if the most recent tweet is not the current date
"""
def refresh_tweets(date):
    return date != datetime.now().strftime("%Y-%m-%d")


def format_tweets_for_company(name, key, tweets):
    tweet_data = []

    for company_tweet in tweets:
        company_json = {}
        company_json['text'] = company_tweet.name
        company_json['sentiment'] = company_tweet.sentiment
        company_json['date'] = company_tweet.date
        tweet_data.append(company_json)

    company_data = {}

    if len(tweets) > 0:
        max_date = datetime.now().strftime("%Y-%m-%d")
        min_date1 = tweets[0].date
        min_date2 = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        min_date = min(min_date1, min_date2)
        company_data = json.loads(engine.get_share_history(key, min_date, max_date))
        min_stock = 1000000
        max_stock = 0
        company_json = {}
        # Get max and min stock for the d3.js graph
        for stock_day in company_data:
            stock_val = float(stock_day["Close"])
            if stock_val > max_stock:
                max_stock = stock_val
            if stock_val < min_stock:
                min_stock = stock_val
        company_json["max"] = max_stock
        company_json["min"] = min_stock
        company_json['history'] = company_data
        company_data = company_json
    result = {'name': name, 'tweets': tweet_data, 'stocks': company_data }
    return result
