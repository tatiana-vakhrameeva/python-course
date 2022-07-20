import unittest
import hashlib
import datetime

from ..utils import cases, MockRedis
import api
from api import INVALID_REQUEST, OK
from store import Store


class TestOnlineScore(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = MockRedis()

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512(
                bytes(
                    datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT,
                    "utf-8",
                )
            ).hexdigest()
        else:
            request["token"] = hashlib.sha512(
                bytes(request.get("account") + request.get("login") + api.SALT, "utf-8")
            ).hexdigest()

    def set_invalid_auth(self, request):
        request["token"] = "invalid_token"

    def get_response(self, request):
        return api.method_handler(
            {"body": request, "headers": self.headers}, self.context, self.store
        )

    @cases(
        [
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "first_name": "Стансилав",
                        "last_name": "Ступников",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                },
                "expected_response": ({"score": 5.0}, OK),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                },
                "expected_response": ({"score": 4.5}, OK),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru"},
                },
                "expected_response": ({"score": 3.0}, OK),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {"first_name": "Стансилав", "last_name": "Ступников"},
                },
                "expected_response": ({"score": 0.5}, OK),
            },
        ]
    )
    def test_get_correct_response(self, args):
        request = args.get("request")
        self.set_valid_auth(request)
        expected_response = args.get("expected_response")

        resp = self.get_response(request)
        self.assertEqual(resp, expected_response)

    @cases(
        [
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "first_name": "Стансилав",
                        "last_name": "Ступников",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                },
                "expected_response": ({"score": 5.0}, OK),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                },
                "expected_response": ({"score": 4.5}, OK),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru"},
                },
                "expected_response": ({"score": 3.0}, OK),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {"first_name": "Стансилав", "last_name": "Ступников"},
                },
                "expected_response": ({"score": 0.5}, OK),
            },
        ]
    )
    def test_get_correct_response_without_redis(self, args):
        self.store = Store(host="unavailable", port=8080)
        request = args.get("request")
        self.set_valid_auth(request)
        expected_response = args.get("expected_response")

        resp = self.get_response(request)
        self.assertEqual(resp, expected_response)

    @cases(
        [
            {
                "request": {},
                "expected_response": (
                    "login -> This field is required",
                    INVALID_REQUEST,
                ),
            },
        ]
    )
    def test_empty_request(self, args):
        request = args.get("request")
        expected_response = args.get("expected_response")

        resp = self.get_response(request)
        self.assertEqual(resp, expected_response)

    @cases(
        [
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru"},
                },
                "expected_response": ("Forbidden", 403),
            },
        ]
    )
    def test_invalid_auth(self, args):
        request = args.get("request")
        self.set_invalid_auth(request)
        expected_response = args.get("expected_response")

        resp = self.get_response(request)
        self.assertEqual(resp, expected_response)

    @cases(
        [
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {
                        "phone": 1234,
                        "email": "stupnikov@otus.ru",
                        "first_name": "Стансилав",
                        "last_name": "Ступников",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                },
                "expected_response": (
                    "phone -> Must contain 11 symbols",
                    INVALID_REQUEST,
                ),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "arguments": {
                        "phone": "79175002040",
                    },
                },
                "expected_response": (
                    "Request should contain one of pairs: Phone + Email, First Name + Last Name or Gender + Birthday",
                    INVALID_REQUEST,
                ),
            },
        ]
    )
    def test_invalid_arguments(self, args):
        request = args.get("request")
        self.set_valid_auth(request)
        expected_response = args.get("expected_response")

        resp = self.get_response(request)
        self.assertEqual(resp, expected_response)
