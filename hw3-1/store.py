import redis


SOCKET_TIMEOUT = 15000


class Store(object):
    def __init__(self, host, port, socket_timeout=SOCKET_TIMEOUT):
        self.r = redis.Redis(host=host, port=port, socket_timeout=socket_timeout)

    def get(self, key):
        return self.r.get(key)

    def cache_get(self, key):
        return self.r.get(key)

    def cache_set(self, key, value, time):
        self.r.set(key, value, ex=time)
