Flask-Language
==============

|PyPI Version| |PyPI License| |PyPI Versions| |Build Status| |Coverage
Status| |Documentation Status|

Flask-Language is a Flask_ extension providing a
simple mechanism to handle a client-side language cookie.

It is somewhat loosely based on this snippet: `<http://flask.pocoo.org/snippets/128>`__

.. _Flask: http://flask.pocoo.org

Installation
------------

Install the extension with with pipenv_ (recommended):

::

    $ pipenv install flask-language

Or with pip_:

::

    $ pip install flask-language

.. _pip: https://pip.pypa.io
.. _pipenv: https://docs.pipenv.org

Usage
-----

Initialize the Flask-Language extension:

::

        from flask import Flask, jsonify
        from flask_language import Language, current_language

        app = Flask(__name__)
        lang = Language(app)

Define the language hooks:

::

        @lang.allowed_languages
        def get_allowed_languages():
            return ['en', 'fr']

        @lang.default_language
        def get_default_language():
            return 'en'

Define the desired end-points to retrieve and manipulate the current language:

::

        @app.route('/api/language')
        def get_language():
            return jsonify({
                'language': str(current_language),
            })

        @app.route('/api/language', methods=['POST'])
        def set_language():
            req = request.get_json()
            language = req.get('language', None)

            lang.change_language(language)

            return jsonify({
                'language': str(current_language),
            })

Before each request, Flask-Language will automatically determine the current
language in the following order:

1. The language cookie (if any and matching the allowed languages)
2. The `Accept-Language` HTTP header (if any and matching the allowed languages)
3. The provided default language

During each request context, the current language can be accessed using
`current_language`.

After each request, the current language will be stored in the language cookie.

.. _Application Factories: http://flask.pocoo.org/docs/0.12/patterns/appfactories/

Configuration
-------------

Flask-Language is configurable via the following configuration variables:

- `LANGUAGE_COOKIE_NAME`: name for the cookie language (default: 'lang')
- `LANGUAGE_COOKIE_TIMEOUT`: validity duration (using `datetime.timedelta`) of the cookie language (default: 365 days)
- `LANGUAGE_COOKIE_DOMAIN`: domain for the cookie language (default: None)
- `LANGUAGE_COOKIE_SECURE`: set secure option for the cookie language (default: False)
- `LANGUAGE_COOKIE_HTTPONLY`: set HTTP-only for the cookie language (default: False)

Documentation
-------------

The Sphinx-compiled documentation is available on
`ReadTheDocs <http://flask-language.readthedocs.io/en/latest/>`__.

License
-------

The MIT License (MIT)

Copyright (c) 2018 Romain Clement

.. |PyPI Version| image:: https://img.shields.io/pypi/v/flask-language.svg
   :target: https://pypi.python.org/pypi/flask-language
.. |PyPI License| image:: https://img.shields.io/pypi/l/flask-language.svg
   :target: https://pypi.python.org/pypi/flask-language
.. |PyPI Versions| image:: https://img.shields.io/pypi/pyversions/flask-language.svg
   :target: https://pypi.python.org/pypi/flask-language
.. |Build Status| image:: https://travis-ci.org/rclement/flask-language.svg?branch=master
   :target: https://travis-ci.org/rclement/flask-language
.. |Coverage Status| image:: https://coveralls.io/repos/github/rclement/flask-language/badge.svg?branch=master
   :target: https://coveralls.io/github/rclement/flask-language?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/flask-language/badge/?version=master
   :target: http://flask-language.readthedocs.io/en/master/
