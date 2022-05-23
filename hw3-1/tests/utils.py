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
