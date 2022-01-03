__version__ = '0.1.0'


import functools, operator


# Same behaviour from `functools.cache` in 3.9+
cache = lambda func: functools.lru_cache(maxsize=None)(func)


def _combine_reduce(get_value, max_before, operation, node, values):
    # We allow "max_before" in case the operation isn't commutative.
    if max_before is None: # avoid duplicating with slices.
        max_before = len(child_values)
    # insert node value in the appropriate place.
    values = values[:max_before] + (get_value(node),) + values[max_before:]
    # There is at least one value, so we don't need an initial value.
    return functools.reduce(operation, values)


def combine_sum_preorder(get_value):
    return functools.partial(_combine_reduce, get_value, 0, operator.add)


def combine_sum_inorder(get_value):
    return functools.partial(_combine_reduce, get_value, 1, operator.add)


def combine_sum_postorder(get_value):
    return functools.partial(_combine_reduce, get_value, None, operator.add)


_combiners = {
    'sum_preorder': combine_sum_preorder,
    'sum_inorder': combine_sum_inorder,
    'sum_postorder': combine_sum_postorder
}


# We have to use a class for this, since with functools.partial
# we would need the partial args to be self-referential
# (one arg would be the partial itself).
class Traverser:
    def __init__(self, get_children, combine, cache):
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
            node, tuple(map(self._recurse, self._get_children(node)))
        )


def _getter(func, attr, item, names, tag):
    if (func, attr, item).count(None) != 2:
        name_labels = ', '.join(f'`{name}`' for name in names)
        requirement = 'exactly one of' if required else 'at most one of'
        raise ValueError(f'{requirement} {{{name_labels}}} {tag}')
    if attr is not None:
        func = operator.attrgetter(attr)
    elif item is not None:
        func = operator.itemgetter(item)
    if not callable(func):
        raise ValueError(
            f'`{name_labels[0]}` (or computed value) must be callable'
        )
    return func


def make_traverser(
    combine, *,
    cache=cache, 
    get_value=None, value_attr=None, value_item=None,
    get_children=None, child_attr=None, child_item=None
):
    get_children = _getter(
        get_children, child_attr, child_item,
        ('get_children', 'child_attr', 'child_item'),
        'must be specified and not None'
    )
    if isinstance(combine, str):
        get_value = _getter(
            get_value, value_attr, value_item,
            ('get_value', 'value_attr', 'value_item'),
            'must be specified and not None when `combine` is a string'
        )
        combine = _combiners[combine](get_value)
    elif not callable(combine):
        raise TypeError(''.join(
            '`combine` must be a lookup string or a callable accepting',
            'a node and a tuple of child results'
        ))
    return Traverser(get_children, combine, cache)


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
