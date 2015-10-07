import csv
from swocker import db
from models import *
import IPython
import os

def find_relevant_key(name):
	array = name.lower().split()
	fluff = [
		'inc.',
		'inc',
		'co.',
		'co',
		'company',
		'llc',
		'the',
		'corp.',
		'corporation',
		'group'
		#TODO add more words here or even do this in a separate script
	]
	for f in fluff:
		if f in array:
			array.pop(array.index(f))
	return ' '.join(array)

def load_companies_into_database():
	files = ['app/exchanges/nasdaq.csv', 'app/exchanges/nyse.csv', 'app/exchanges/amex.csv']
	for file_name in files:
		reader = csv.reader(open(file_name))
		#Skip the first line
		reader.next()
		for row in reader:
			try:
				new_company = Company(name=find_relevant_key(row[1].lower()),code=row[0].upper())
				db.session.add(new_company)
				db.session.commit()
			except Exception:
				db.session.rollback()
				continue
