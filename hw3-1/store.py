import redis

RECONNECT_DELAY = 1000
SOCKET_TIMEOUT = 15000
RECONNECT_MAX_ATTEMPTS = 3


class Store(object):
    def __init__(
        self,
        host,
        port,
        socket_timeout=SOCKET_TIMEOUT,
        reconnect_max_attempts=RECONNECT_MAX_ATTEMPTS,
        reconnect_delay=RECONNECT_DELAY,
    ):

        self.r = redis.Redis(
            host, port, socket_timeout, reconnect_max_attempts, reconnect_delay
        )

    def get(self, key):
        return self.r.get(key)

    def cached_get():
        pass

    def cache_set(self, key, value, time):
        self.r.set(key, value, keepttl=time)
