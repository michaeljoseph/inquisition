# inquisition

## Nobody expects the Code Review Inquisition!

![no one expected this](http://24.media.tumblr.com/tumblr_m4jru1wwGS1qmfjj7o1_500.jpg)

## Overview

This Flask webapp presents users, across a GitHub organisation's repositories:

- ranked by the number of pull request creations and pull request comments
- lists currently open pull requests across repos in an organisation


## Installation and Setup

### Setup

    $ git clone https://github.com/michaeljoseph/inquisition.git
    $ cd inquisition; virtualenv .; source bin/activate
    $ pip install -r requirements.txt

### Configure

Edit config.py and change `GITHUB_TOKEN` and `ORGANISATION_NAME`

    DEBUG = True
    TESTING = True
    SECRET_KEY = 'the key to secrecy is a secret key'
    GITHUB_TOKEN = "db3845dbff6a4f14b77ebbe890edd989"
    STORE = '.'
    ORGANISATION_NAME = 'my-organisation-name'

### Initialise the data store

	$ python -c 'import store, config; store.load_data(config.ORGANISATION_NAME)'

### Run it

    $ python app.py
