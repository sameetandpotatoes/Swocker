from celery import Celery
from swocker import db, models, engine
from flask import Flask
from datetime import timedelta
from alchemyapi import AlchemyAPI

# celery = Celery('app', broker='amqp://guest@localhost//')
def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

#Example of how celerybeat schedule should be organized
# 'add-every-30-seconds': {
#     'task': 'app.tasks.add',
#     'schedule': timedelta(seconds=5),
#     'args': (16, 16)
# },

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://guest@localhost//',
    CELERY_RESULT_BACKEND='amqp://guest@localhost//',
    CELERYBEAT_SCHEDULE = {
        'store-tweets-every-day': {
            'task': 'app.tasks.store_tweets_in_database',
            'schedule': timedelta(days=1)
        },
    },
    CELERY_TIMEZONE = 'UTC',
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_ENABLE_UTC = True
)
celery = make_celery(app)

@celery.task()
def add(x, y):
    print(x + y)
    return x + y

@celery.task()
def store_tweets_in_database():
    for company in models.Company.query.filter(models.Company.retrieved_data==False).all():
        print "---\nLooking at " + company.name + "\n---\n"

        tweets, tweets_list = engine.twit_search(company.name)
        if tweets is None:
            company_id_start = company.id
            print "Twitter api is overused"
            print "---\nStopping at company " + str(company_id_start) + " : " + company.name + "\n---\n"
            return

        # related_words = generate_concepts_for_company(company.id, tweets_list)

        # if related_words is None:
        #     company_id_start = company.id
        #     print "No related words"
        #     print "---\nStopping at company " + str(company_id_start) + " : " + company.name + "\n---\n"
        #     return

        for tweet in tweets:
            if not store_sentiment_for_tweet(company.id, tweet):
                print "Failed to store sentiment"
                print "---\nStopping at company " + str(company_id_start) + " : " + company.name + "\n---\n"
                return

        print "---\n" + company.name + "'s Tweets \n---"
        for t in models.Tweet.query.filter_by(company_id=company.id):
            print(t.name + " : " +str(t.sentiment))
        company.retrieved_data = True

    # at the end set them all back to false
    for company in models.Company.query.all():
        company.retrieved_data = False

def generate_concepts_for_company(company_id, tweets):
    all_tweets_as_string = ' '.join(tweets)
    alchemyapi = AlchemyAPI()
    api_error = False
    for apikey in engine.get_random_alchemy_credentials():
        alchemyapi.apikey = apikey
        response = alchemyapi.concepts('text', all_tweets_as_string)
        related_words = []
        if response['status'] == 'OK':
            for concept in response['concepts']:
                related_words.append(concept['text'])
        elif response['status'] == 'ERROR' and tweets != []:
            print "ERROR getting concepts" + response['statusInfo']
            api_error = True
            # Move onto the next api key
            continue
    # Return null when all api keys are exhausted
    if api_error and len(related_words) == 0:
        return None
    return related_words

def store_sentiment_for_tweet(company_id, tweet):
    sentiment = get_sentiment(company_id, tweet['text'])
    if sentiment is None:
        return False
    new_tweet = models.Tweet(name=tweet['text'],date=tweet['date'],sentiment=sentiment,company_id=company_id)
    try:
        db.session.add(new_tweet)
        db.session.commit()
    except Exception:
        db.session.rollback()
    return True

"""
Returns sentiment for a tweet as a rounded decimal, None if api limit exceeded
"""
def get_sentiment(company_id, text):
    alchemyapi = AlchemyAPI()
    key_phrases = []
    for apikey in engine.get_random_alchemy_credentials():
        alchemyapi.apikey = apikey
        response = alchemyapi.keywords('text', text, {'sentiment': 1})
        if response['status'] == 'OK':
            if len(response['keywords']) == 0:
                return 0
            # related_words = models.RelatedWord.query.filter_by(company_id=company_id).all()
            for keyword in response["keywords"]:
                if 'sentiment' in keyword:
                    if keyword['sentiment'].has_key('score'):
                        key_phrases.append(float(keyword['sentiment']['score']))
                    elif keyword['sentiment']['type'] == 'neutral':
                        key_phrases.append(0)

            if len(key_phrases) == 0:
                return 0
            else:
                return float("{0:.2f}".format(sum(key_phrases)/len(key_phrases)))
        elif response['status'] == 'ERROR' and response['statusInfo'] != 'unsupported-text-language':
            print "ERROR: getting sentiment " + response['statusInfo']
            # Skip onto the next api key
            continue
        else:
            print "None of the above " + response['statusInfo']
            return 0
    #Return none when all api keys are exhausted
    return None
