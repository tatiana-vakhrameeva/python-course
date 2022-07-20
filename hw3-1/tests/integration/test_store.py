import os
import unittest
from unittest.case import skipIf

from store import Store

redis_host = os.environ.get("REDIS_HOST", False)
redis_port = os.environ.get("REDIS_PORT", False)


@skipIf(not (redis_host and redis_port), "Store connection parameters weren't passed")
class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = Store(host=redis_host, port=redis_port)

    def test_get(self):
        expected_value = "value from redis"
        key = "key_1"

        self.store.set(key, expected_value, 60 * 60)

        res = self.store.get(key).decode("utf-8")
        self.assertEqual(res, expected_value)

    def test_cache_get(self):
        expected_value = "value from redis"
        key = "key_2"

        self.store.set(key, expected_value, 60 * 60)

        res = self.store.cache_get(key).decode("utf-8")

        self.assertEqual(res, expected_value)

    def test_cache_set(self):
        expected_value = "value from redis"
        key = "key_3"

        self.store.cache_set(key, expected_value, 60 * 60)

        res = self.store.cache_get(key).decode("utf-8")

        self.assertEqual(res, expected_value)
