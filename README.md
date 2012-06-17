# inquisition

## No one expects the Code Review Inquisition!

![no one expected this](http://24.media.tumblr.com/tumblr_m4jru1wwGS1qmfjj7o1_500.jpg)

## Overview

This Flask webapp presents users, across a GitHub organisation's repositories:

- ranked by the number of pull request creations and pull request comments
- lists currently open pull requests across repos in an organisation

[Demonstration site @ http://theinquisition.herokuapp.com](http://theinquisition.herokuapp.com/)


## Installation and Setup

### Setup

    $ git clone https://github.com/michaeljoseph/inquisition.git
    $ cd inquisition; virtualenv .; source bin/activate
    $ pip install -r requirements.txt

### Configure

Edit config.py and change `GITHUB_USER`, `GITHUB_PASSWORD` and `ORGANISATION_NAME`

	DEBUG = True
	TESTING = True
	SECRET_KEY = 'the key is secrecy is a secret key'
	
	# Github credentials
	GITHUB_USER = 'a-github-username'
	GITHUB_PASSWORD = 'a-github-password'
	ORGANISATION_NAME = 'an-organisation-name'
	
	# The directory to store the github json data file
	STORE = '.'

### Initialise the data store

	$ python -c 'import store, config; store.load_data(config.ORGANISATION_NAME, update=True)'

### Run it

    $ python app.py

### Deploy

I've included a setup script (that works for me, YMMV, IANAL) targeted at Ubuntu server environments (using nginx and gunicorn). Configure it by editing ``scripts/setup.sh`` and setting these variables for your environment.

    SOURCE_DIRECTORY=.
    HOSTNAME=inquisition.example.com
    INQUISITION_ROOT=/srv/www/inquisition


You'll probably also want to keep the local data store up-to-date, so cron re-loading the data:

    # m h  dom mon dow   command
    @hourly INQUISITION_ROOT=/srv/www/inquisition PYTHONPATH=$INQUISITION_ROOT $INQUISITION_ROOT/bin/python -c "import store; store.load_data(config.ORGANISATION_NAME, update=True)"


