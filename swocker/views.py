from flask import Flask, flash, jsonify, render_template, redirect
from swocker import app, engine, company, sentiment, tasks, helper
from swocker.models import *
import json
import IPython
import time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/company/<company_code>')
def graph(company_code):
    key = company.find_relevant_key(company_code)
    queried_company = Company.query.filter_by(code=key.upper()).first()
    if queried_company == None:
        #Return error
        flash('Invalid company name. Try typing a correct company code')
        return redirect('/')

    tweets = queried_company.tweets.order_by('date').all()
    if len(tweets) > 0:
        result = helper.format_tweets_for_company(key, tweets)
        return render_template('graph.html', data=json.dumps(result))
    elif len(tweets) == 0 and tasks.store_tweets_by_company(queried_company):
        return redirect('/company/'+company_code)
    else:
        #Return error
        flash('Invalid company name. Try typing a correct company code')
        return redirect('/')
