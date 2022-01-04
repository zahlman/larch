__version__ = '0.1.0'


import functools, operator
from .cache import cache, unique_cache
from .combine import get_combiner


# The recursion algorithm is pulled out as a separate function so that
# each Traverser instance can decorate it with its own cache and the
# recursive calls can use the decorated version.
# Doing it this way instead of using `__call__` allows the cache to give
# results immediately on future requests rather than doing one recursion step.
def _recurse(traverser, node):
    return traverser._combine(
        traverser._get_value(node),
        tuple(map(traverser._recurse, traverser._get_children(node)))
    )


# We have to use a class for this, since with functools.partial
# we would need the partial args to be self-referential
# (one arg would be the partial itself).
class Traverser:
    def __init__(self, get_children, get_value, combine, cache):
        self._get_children = get_children
        self._get_value = get_value
        self._combine = combine
        if cache is None:
            self._recurse = functools.partial(_recurse, self)
            self._clear = lambda: None
        else:
            self._recurse = cache(functools.partial(_recurse, self))
            self._clear = self._recurse.cache_clear


    def clear_cache(self):
        self._clear()


    def __call__(self, node):
        return self._recurse(node)


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
    # TODO: allow this to be None.
    get_value = _getter(
        get_value, value_attr, value_item,
        ('get_value', 'value_attr', 'value_item'),
        'must be specified and not None'
    )
    if isinstance(combine, str):
        combine = get_combiner(combine)
    elif not callable(combine):
        raise TypeError(''.join(
            '`combine` must be a lookup string or a callable accepting',
            'a node and a tuple of child results'
        ))
    return Traverser(get_children, get_value, combine, cache)
