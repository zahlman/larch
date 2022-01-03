import functools


# Same behaviour from `functools.cache` in 3.9+
cache = lambda func: functools.lru_cache(maxsize=None)(func)


def unique_cache(dummy=0):
    def decorator(traverse_func):
        seen = set()
        @functools.wraps(traverse_func)
        def cached(node):
            if node in seen:
                return dummy
            seen.add(node)
            return traverse_func(node)    
        cached.cache_clear = seen.clear
        return cached
    return decorator
