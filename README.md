# Mendeley API Python Example #

This is a simple example of an application that consumes the [Mendeley](http://www.mendeley.com) API, using the [Python SDK](http://mendeley-python.readthedocs.org/).

For more information on the API, see the [developer portal](http://dev.mendeley.com).

## About the application ##

The application is a website that allows you to see the documents in your Mendeley library, together with their annotations.  It also allows you to look up a document by [DOI](http://www.doi.org/).

It's built with [Flask](http://flask.pocoo.org/) and [Jinja2](http://jinja.pocoo.org/docs/).

## How to run ##

1. Install [Python](https://www.python.org/) and [Pip](https://pip.pypa.io/en/latest/).
2. Register your client at the [developer portal](http://dev.mendeley.com). Use `http://localhost:5000/oauth` as your  Redirect URI. This will give you a client ID and secret.
3. Rename the config.yml.example file to config.yml, and fill in your client ID and secret in this file.
4. Run the following command to install dependencies:

        pip install -r requirements.txt

5. Start the server:

		python mendeley-example.py

6. Go to http://localhost:5000 in your browser.

## Build status ##

![Travis CI](https://travis-ci.org/Mendeley/mendeley-api-python-example.svg?branch=master)
