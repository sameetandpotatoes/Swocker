from flask import Flask, flash, jsonify, render_template
from swocker import app, engine, company, sentiment
from swocker.models import *
import json
import IPython

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/company/<company_code>')
def graph(company_code):
    key = company.find_relevant_key(company_code)
    queried_company = Company.query.filter_by(code=key.upper()).all()[0]
    tweets = queried_company.tweets.order_by('date').all()
    tweet_data = []

    for company_tweet in tweets:
        company_json = {}
        company_json['text'] = company_tweet.name
        company_json['sentiment'] = company_tweet.sentiment
        company_json['date'] = company_tweet.date
        tweet_data.append(company_json)

    company_data = {}

    if len(tweets) > 0:
        min_date = tweets[0].date
        max_date = tweets[len(tweets) - 1].date
        company_data = json.loads(engine.get_share_history(key, min_date, max_date))
        min_stock = 1000000
        max_stock = 0
        company_json = {}
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

    result = {'tweets': tweet_data, 'stocks': company_data }
    return render_template('graph.html', data=json.dumps(result))

#Actually never needed, kept for fun I guess?
@app.route('/symbol/<company_symbol>/')
def get_stock_info(company_symbol):
	return engine.get_share_price(company_symbol)

@app.route('/history/<company_symbol>/<start_date>/<end_date>/')
def get_history(company_symbol, start_date, end_date):
	return engine.get_share_history(company_symbol, start_date, end_date)
