import redis
import logging


SOCKET_TIMEOUT = 15000


class Store(object):
    def __init__(self, host, port, socket_timeout=SOCKET_TIMEOUT):
        self.r = redis.Redis(host=host, port=port, socket_timeout=socket_timeout)

    def get(self, key):
        return self.r.get(key)

    def cache_get(self, key):
        try:
            return self.r.get(key)
        except Exception as e:
            logging.exception("Can't get from cache: %s" % e)
            return None

    def cache_set(self, key, value, time):
        try:
            self.r.set(key, value, ex=time)
        except Exception as e:
            logging.exception("Can't set to cache: %s" % e)
