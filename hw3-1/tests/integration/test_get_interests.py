import unittest
import hashlib
import datetime

from ..utils import cases, MockRedis
import api
from api import INVALID_REQUEST, OK
from store import Store


class TestGetInterests(unittest.TestCase):
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
                "request": {},
                "expected_response": (
                    "login -> This field is required",
                    INVALID_REQUEST,
                ),
            },
        ]
    )
    def test_empty_request(self, args):
        mocked_interests = {
            "i:1": '"yoga"',
            "i:2": '"drums"',
            "i:3": '"programing"',
            "i:4": '"coffee"',
        }
        for key, value in mocked_interests.items():
            self.store.set(key, value)

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
                    "method": "clients_interests",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": ""},
                },
                "expected_response": ("Forbidden", 403),
            },
        ]
    )
    def test_invalid_auth(self, args):
        mocked_interests = {
            "i:1": '"yoga"',
            "i:2": '"drums"',
            "i:3": '"programing"',
            "i:4": '"coffee"',
        }
        for key, value in mocked_interests.items():
            self.store.set(key, value)

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
                    "method": "somemethod",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": ""},
                },
                "expected_response": ("Unknown method", INVALID_REQUEST),
            },
        ]
    )
    def test_invalid_method_request(self, args):
        mocked_interests = {
            "i:1": '"yoga"',
            "i:2": '"drums"',
            "i:3": '"programing"',
            "i:4": '"coffee"',
        }
        for key, value in mocked_interests.items():
            self.store.set(key, value)

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
                    "method": "clients_interests",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": "invalid date"},
                },
                "expected_response": (
                    "date -> Must be in DD.MM.YYYY format",
                    INVALID_REQUEST,
                ),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "clients_interests",
                    "arguments": {"client_ids": "array", "date": ""},
                },
                "expected_response": (
                    "client_ids -> This field must array of int",
                    INVALID_REQUEST,
                ),
            },
        ]
    )
    def test_invalid_arguments(self, args):
        mocked_interests = {
            "i:1": '"yoga"',
            "i:2": '"drums"',
            "i:3": '"programing"',
            "i:4": '"coffee"',
        }
        for key, value in mocked_interests.items():
            self.store.set(key, value)

        request = args.get("request")
        self.set_valid_auth(request)
        expected_response = args.get("expected_response")

        resp = self.get_response(request)
        self.assertEqual(resp, expected_response)

    @cases(
        [
            {
                "request": {
                    "account": 2022,
                    "login": "h&f",
                    "method": "clients_interests",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": "invalid date"},
                },
                "expected_response": (
                    "account -> This field must be string",
                    INVALID_REQUEST,
                ),
            },
            {
                "request": {
                    "account": "horns&hoofs",
                    "login": 7274,
                    "method": "clients_interests",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": "invalid date"},
                },
                "expected_response": (
                    "login -> This field must be string",
                    INVALID_REQUEST,
                ),
            },
        ]
    )
    def test_invalid_fields(self, args):
        mocked_interests = {
            "i:1": '"yoga"',
            "i:2": '"drums"',
            "i:3": '"programing"',
            "i:4": '"coffee"',
        }
        for key, value in mocked_interests.items():
            self.store.set(key, value)

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
                    "method": "clients_interests",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": ""},
                },
                "expected_response": (
                    {1: "yoga", 2: "drums", 3: "programing", 4: "coffee"},
                    OK,
                ),
            },
        ]
    )
    def test_get_correct_response(self, args):
        mocked_interests = {
            "i:1": '"yoga"',
            "i:2": '"drums"',
            "i:3": '"programing"',
            "i:4": '"coffee"',
        }
        for key, value in mocked_interests.items():
            self.store.set(key, value)

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
                    "method": "clients_interests",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": ""},
                }
            }
        ]
    )
    def test_store_unavailable(self, args):
        self.store = Store(host="unavailable", port=8080)

        request = args.get("request")
        self.set_valid_auth(request)

        with self.assertRaises(Exception):
            self.get_response(request)
