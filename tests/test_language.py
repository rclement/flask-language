import unittest
import json

try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie

from flask import Flask, jsonify, request
from flask_language import Language, current_language


# ------------------------------------------------------------------------------


class JSONRequest:
    def __init__(self, data):
        self.json = json.dumps(data)
        self.content_type = 'application/json'


def get_json_data(response):
    return json.loads(response.data)


def get_cookies(response):
    return SimpleCookie(response.headers.get('set-cookie'))


# ------------------------------------------------------------------------------


class TestLanguage(unittest.TestCase):

    def assert_language_response(self, response, lang):
        cookies = get_cookies(response)
        cookie_lang = cookies.get(self.lang._cookie_name)
        self.assertNotEqual(cookie_lang, None)
        self.assertEqual(cookie_lang.value, lang)

        data = get_json_data(response)
        self.assertEqual(data.get('language'), lang)

    def setUp(self):
        app = Flask(__name__)
        app.testing = True
        self.app = app
        self.client = app.test_client(use_cookies=True)
        self.lang = Language(app)
        self.allowed_languages = ['en', 'fr']
        self.default_language = 'en'

        @self.lang.allowed_languages
        def allowed_languages():
            return self.allowed_languages

        @self.lang.default_language
        def default_language():
            return self.default_language

        @self.app.route('/language')
        def get_language():
            return jsonify({
                'language': str(current_language)
            }), 200

        @self.app.route('/language', methods=['POST'])
        def set_language():
            req = request.get_json()
            language = req.get('language', None)

            self.lang.change_language(language)

            return jsonify({
                'language': str(current_language),
            }), 201

    def test_get_default_language(self):
        rv = self.client.get('/language')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.mimetype, 'application/json')
        self.assert_language_response(rv, self.default_language)

    def test_change_allowed_language(self):
        new_lang = 'fr'

        rq = JSONRequest({
            'language': new_lang
        })

        rv = self.client.post(
            '/language', data=rq.json, content_type=rq.content_type
        )
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rv.mimetype, 'application/json')
        self.assert_language_response(rv, new_lang)

    def test_change_not_allowed_language(self):
        new_lang = 'dk'

        rq = JSONRequest({
            'language': new_lang
        })

        rv = self.client.post(
            '/language', data=rq.json, content_type=rq.content_type
        )
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rv.mimetype, 'application/json')
        self.assert_language_response(rv, self.default_language)


if __name__ == '__main__':
    unittest.main()
