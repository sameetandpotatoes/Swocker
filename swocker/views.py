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

    company_data = json.loads(engine.get_share_history(key, '2015-09-28', '2015-10-07'))
    result = {'tweets': tweet_data, 'stocks': company_data }
    return render_template('graph.html', data=json.dumps(result))

@app.route('/graph')
def graph_view():
    return render_template('graph.html')

@app.route('/symbol/<company_symbol>/')
def get_stock_info(company_symbol):
	return engine.get_share_price(company_symbol)

@app.route('/history/<company_symbol>/<start_date>/<end_date>/')
def get_history(company_symbol, start_date, end_date):
	return engine.get_share_history(company_symbol, start_date, end_date)
