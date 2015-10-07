import json

def average_sentiment_per_day(tweets_with_sentiment):
	tweets = json.loads(tweets_with_sentiment)
	avg = {}
	vals = {}
	dates = []
	for tweet in tweets:
		if tweet['date'] not in avg:
			avg[tweet['date']] = tweet['sentiment']
			vals[tweet['date']] = 1
			dates.append(tweet['date'])
		else:
			avg[tweet['date']] += tweet['sentiment']
			vals[tweet['date']] += 1
	for date in dates:
		avg[date] /= vals[date]
	return avg