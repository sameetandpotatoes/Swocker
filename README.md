Dependencies:
=======
Install `command line tools`:

    xcode-select –install

Install `brew`:

    ruby -e “$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)”

    brew doctor

Install `Python (2.7)`:

    brew install python

Install `virtualenv`:

    pip install virtualenv

Install [`mysql (5.5)`](https://dev.mysql.com/downloads/mysql/5.5.html)

Downloading the Code
===

    git clone https://github.com/sameetandpotatoes/Swocker.git

Make sure you have run `bin/activate` to activate the virtualenv, and then run the following commands to install all necessary dependencies inside the virtualenv:

    pip install -r requirements.txt

###`secrets.py` is organized like this inside the swocker folder:###

    ALCHEMY_CODES = [
        ''
    ]
    TWITTER_CODES = [
        {
            'CONSUMER_KEY': '',
            'CONSUMER_SECRET': '',
            'ACCESS_TOKEN': '',
            'ACCESS_SECRET': ''
        },
    ]

Create a file `secrets.py` in the app directory with `touch secrets.py`, and copy the default format.

Fill in your API keys, we'll collect everyone's when we deploy / store them as environment variables in production eventually

### Creating the Database

**Note: You only have to do this if there isn't an app.db file. Basically, ignore the rest of the instructions, this is just things that I had to do to get things working**

- Run `python db_create.py` to create the database
- Run `python db_migrate.py` to migrate the database
- Open up the python shell (On Mac, just type `python`)
- `from swocker import company`
- `company.load_objects_into_database()`
- All companies are now created. You can see them all with:
- `from swocker.models import *`
- `Company.query.all()`
- Now, to get some tweets in there:
- `from swocker import tasks`
- `tasks.store_tweets_in_database()`

This won't complete all the way. Wait about a day, then rerun.

## RabbitMQ and Celery Set Up:

To get this running on a deployed server, you need RabbitMQ and Celery. If you want to try to simulate this on your computer, you need all three of these commands running at the same time:

- `rabbitmq-server`
- `celery -A app.tasks.celery worker --loglevel=info`
- `celery -A app.tasks.celery beat`

You won't see anything for a day or so (you can change the frequency of the task if you want in `tasks.py`)

- `Ctrl + D` to exit the shell


Running the App
===

- Then run the app with `python app.py`. You'll see data instantly for the companies that we have tweets for!
