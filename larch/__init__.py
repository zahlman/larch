__version__ = '0.1.0'


import functools


# Same behaviour from `functools.cache` in 3.9+
cache = lambda func: functools.lru_cache(maxsize=None)(func)


# We have to use a class for this, since with functools.partial
# we would need the partial args to be self-referential
# (one arg would be the partial itself).
class Traverser:
    def __init__(self, get_children, combine, cache=cache):
        self._get_children = get_children
        self._combine = combine
        if cache is None:
            self._recurse = self.__call__
            self._clear = lambda: None
        else:
            self._recurse = cache(self.__call__)
            self._clear = self._recurse.cache_clear


    def clear_cache(self):
        self._clear()


    def __call__(self, node):
        return self._combine(
            node,
            tuple(
                self._recurse(child)
                for child in self._get_children(node)
            )
        )


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
