from flask import Flask, flash, jsonify, render_template, redirect
from swocker import app, engine, company, sentiment, tasks, helper
from swocker.models import *
from sqlalchemy import or_
import json
import IPython
import time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/company/<company_code>')
def graph(company_code):
    key = company.find_relevant_key(company_code)
    queried_company = Company.query.filter(or_(Company.name.like(key), Company.code.like(key.upper()))).first()


    if queried_company == None:
        #Return error
        flash('Invalid company name. Try typing a correct company code')
        return redirect('/')

    # Now set the actual key
    key = queried_company.code

    tweets = queried_company.tweets.order_by(Tweet.date.desc()).all()

    refresh = False

    if len(tweets) > 0:
        most_recent_tweet = tweets[0].date
        refresh = helper.refresh_tweets(most_recent_tweet)

    if (len(tweets) > 0 and not(refresh)) or tasks.store_tweets_by_company(queried_company):
        result = helper.format_tweets_for_company(key, tweets)
        return render_template('graph.html', data=json.dumps(result))
    else:
        #Return error
        flash('Invalid company name. Try typing a correct company code')
        return redirect('/')
