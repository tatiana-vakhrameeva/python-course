import redis
import logging
import time


SOCKET_TIMEOUT = 15000
CONNECTION_MAX_ATTEMPTS = 5


def retry(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.exception("Retry of %s faild: %s" % (func.__name__, e))
                    attempt += 1
                    time.sleep(1)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class Store(object):
    def __init__(self, host, port, socket_timeout=SOCKET_TIMEOUT):
        try:
            self.r = redis.Redis(host=host, port=port, socket_timeout=socket_timeout)
        except Exception as e:
            logging.exception("Can't init store: %s" % e)

    @retry(CONNECTION_MAX_ATTEMPTS)
    def get(self, key):
        return self.r.get(key)

    @retry(CONNECTION_MAX_ATTEMPTS)
    def set(self, key, value, time):
        self.r.set(key, value, ex=time)

    def cache_get(self, key):
        try:
            return self.get(key)
        except Exception as e:
            logging.exception("Can't get from cache: %s" % e)
            return None

    def cache_set(self, key, value, time):
        try:
            self.set(key, value, time)
        except Exception as e:
            logging.exception("Can't set to cache: %s" % e)
