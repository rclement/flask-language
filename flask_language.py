'''
    Flask-Language
    --------------

    Flask-Language is a Flask extension providing a simple mechanism to handle
    a client-side language cookie.

    It is somewhat loosely based on this snippet:
    http://flask.pocoo.org/snippets/128

    :copyright: (c) 2018 by Romain Clement.
    :license: MIT, see LICENSE for more details.
'''


from datetime import timedelta

from flask import _request_ctx_stack as stack, request
from werkzeug.local import LocalProxy


__all__ = ['Language', 'current_language']


_ctx_err_msg = '''
Working outside of an application context.
'''


def _set_language(language):
    ctx = stack.top
    if ctx is None:
        raise RuntimeError(_ctx_err_msg)
    setattr(ctx, 'language', language)


def _find_language():
    ctx = stack.top
    if ctx is None:
        raise RuntimeError(_ctx_err_msg)
    return getattr(ctx, 'language', None)


current_language = LocalProxy(_find_language)


class Language(object):
    '''
    Primary class container for language cookie handling.

    Before each request, it will try to retrieve the current language in the
    language cookie. If no cookie is present, it will try to find a best match
    of allowed languages in the 'Accept-Language' HTTP header. Finally if still
    no language is found, it will use the provided default language.

    Each view can then access the current language using `current_language`.

    After each request, the current language will be stored in the language
    cookie.

    You might initialize :class:`Language` like this::

        language = Language()

    Then pass the application object to be configured::

        language.init_app(app)
    '''

    def __init__(self, app=None):
        self._allowed_languages = None
        self._default_language = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        '''
        Initializes a Flask object `app`: binds language cookie retrieval with
        app.before_request and binds language cookie installation with
        app.after_request.

        :param app: The Flask application object.
        '''

        app.before_request(self._before_request)
        app.after_request(self._after_request)

        self._cookie_name = app.config.get('LANGUAGE_COOKIE_NAME', 'lang')
        self._cookie_timeout = app.config.get('LANGUAGE_COOKIE_TIMEOUT',
                                              timedelta(days=365))
        self._cookie_domain = app.config.get('LANGUAGE_COOKIE_DOMAIN', None)
        self._cookie_secure = app.config.get('LANGUAGE_COOKIE_SECURE', False)
        self._cookie_httponly = app.config.get('LANGUAGE_COOKIE_HTTPONLY',
                                               False)

        return self

    def allowed_languages(self, callback):
        '''
        A decorator to be used to specify the list of allowed languages.

        Example usage of :class:`allowed_languages` might look like this::

            language = Language(app)

            @language.allowed_languages
            def get_allowed_languages():
                return ['en', 'fr']

        :param callback: The callback to be wrapped by the decorator.
        '''

        self._allowed_languages = callback
        return callback

    def default_language(self, callback):
        '''
        A decorator to be used to specify the default language.

        Example usage of :class:`default_language` might look like this::

            language = Language(app)

            @language.default_language
            def get_default_language():
                return 'en'

        :param callback: The callback to be wrapped by the decorator.
        '''

        self._default_language = callback
        return callback

    def change_language(self, language):
        '''
        Allows to change the current language to the specified one.
        The `current_language` will reflect the provided language only if it is
        present in :class:`allowed_languages`.

        Example usage of :class:`change_language` might look like this::

            language = Language(app)

            @app.route('/api/language', methods=['POST'])
            def set_language():
                req = request.get_json()
                lang = req.get('lang')

                language.change_language(lang)

                return jsonify({
                    'lang': str(current_language)
                })

        :param language: The new language to be set.
        '''
        allowed_languages = self._allowed_languages()
        if language in allowed_languages:
            _set_language(language)

    def _before_request(self):
        '''
        Retrieve the current language using the following policy:
            1. Try to extract the language cookie
            2. If no language cookie is found, try to find a match between
               `request.accept_languages` and :class:`allowed_languages`
            3. If no match is found, use the :class:`default_language`

        Afterwards, the `current_language` will be available.
        '''

        if self._allowed_languages is None:
            raise RuntimeError(
                '''
                Specify a callback to retrieve the allowed languages, using the
                allowed_languages decorator.
                '''
            )

        if self._default_language is None:
            raise RuntimeError(
                '''
                Specify a callback to retrieve the default language, using the
                default_language decorator.
                '''
            )

        allowed_languages = self._allowed_languages()
        default_language = self._default_language()

        cookie_lang = request.cookies.get(self._cookie_name)
        request_lang = request.accept_languages.best_match(allowed_languages)
        language = cookie_lang or request_lang or default_language

        _set_language(language)

    def _after_request(self, response):
        '''
        Retrieve the current language and store the value in the language
        cookie.

        :param response: A Flask Response object.
        '''

        lang = _find_language()
        if lang is not None:
            response.set_cookie(key=self._cookie_name,
                                value=lang,
                                max_age=self._cookie_timeout,
                                domain=self._cookie_domain,
                                secure=self._cookie_secure,
                                httponly=self._cookie_httponly)
        return response
