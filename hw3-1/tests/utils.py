import functools


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception as e:
                    e.args = (f"Failed {f.__name__} in with args: {c}", *e.args)
                    raise

        return wrapper

    return decorator


class MockRedis:
    def __init__(self, cache=dict()):
        self.cache = cache

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        return None

    def set(self, key, value, *args, **kwargs):
        if self.cache is not None:
            self.cache[key] = value
            return "OK"
        return None

    def cache_get(self, key):
        if key in self.cache:
            return self.cache[key]
        return None

    def cache_set(self, key, value, *args, **kwargs):
        if self.cache is not None:
            self.cache[key] = value
            return "OK"
        return None
