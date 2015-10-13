from flask import Flask, flash, jsonify, render_template, redirect
from swocker import app, engine, company, sentiment, tasks, helper
from swocker.models import *
from sqlalchemy import or_, func
import json
import IPython
import time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/company/<company_code>')
def graph(company_code):
    key = company.find_relevant_key(company_code)

    for queried_company in Company.query.filter(or_(func.lower(Company.name).contains(func.lower(key)), Company.code.like(key.upper()))).all():        # Now set the actual key
        key = queried_company.code

        tweets = queried_company.tweets.order_by(Tweet.date.desc()).all()
        refresh = False

        if len(tweets) > 0:
            most_recent_tweet = tweets[0].date
            refresh = helper.refresh_tweets(most_recent_tweet)

        background_task_result = False
        if refresh:
            background_task_result = tasks.store_tweets_by_company(queried_company)

        if (len(tweets) > 0 and not(refresh)) or background_task_result:
            tweets = queried_company.tweets.order_by(Tweet.date.desc()).all()
            result = helper.format_tweets_for_company(queried_company.name, key, tweets)
            return render_template('graph.html', data=json.dumps(result))
        else:
            print "Looks like that didn't work. Trying another one"
    #Return error
    flash('Invalid company name. Try typing a correct company code')
    return redirect('/')
