import unittest
from unittest.mock import Mock, call

from store import Store


class TestStore(unittest.TestCase):
    def test_get(self):
        expected_value = "value from redis"
        mock_redis = Mock()
        mock_redis.get.return_value = expected_value

        store = Store(host="host", port=8080)
        store.r = mock_redis

        res = store.get("any_key")
        self.assertEqual(res, expected_value)
        mock_redis.get.assert_called_once()

    def test_cache_get(self):
        expected_value = "value from redis"
        mock_redis = Mock()
        mock_redis.get.return_value = expected_value

        store = Store(host="host", port=8080)
        store.r = mock_redis

        res = store.cache_get("any_key")
        self.assertEqual(res, expected_value)
        mock_redis.get.assert_called_once()

    def test_set(self):
        mock_redis = Mock()

        store = Store(host="host", port=8080)
        store.r = mock_redis
        mock_redis.set = Mock()

        store.set("any_key", "any_value", 60)
        mock_redis.set.assert_called_once()

    def test_cache_set(self):
        mock_redis = Mock()

        store = Store(host="host", port=8080)
        store.r = mock_redis
        mock_redis.set = Mock()

        store.cache_set("any_key", "any_value", 60)
        mock_redis.set.assert_called_once()

    def test_get_retry(self):
        key = "any_key"
        expected_value = "value from redis"
        mock_redis = Mock()
        mock_redis.get.side_effect = [Exception, expected_value]

        store = Store(host="host", port=8080)
        store.r = mock_redis

        res = store.get(key)
        self.assertEqual(res, expected_value)
        mock_redis.get.assert_has_calls([call(key), call(key)])

    def test_set_retry(self):
        mock_redis = Mock()

        store = Store(host="host", port=8080)
        store.r = mock_redis
        mock_redis.set.side_effect = [Exception, "ok"]

        store.cache_set("any_key", "any_value", 60)
        mock_redis.set.assert_has_calls(
            [call("any_key", "any_value", ex=60), call("any_key", "any_value", ex=60)]
        )
