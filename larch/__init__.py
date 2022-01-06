__version__ = "0.1.0+25"


import functools, operator
from .cache import cache, unique_cache
from .combine import get_combiner
from .traversal import get_visitor


# We have to use a class for this, since with functools.partial
# we would need the partial args to be self-referential
# (one arg would be the partial itself).
class Traverser:
    def __init__(self, visit, combine, cache):
        self._visit = visit
        self._combine = combine
        if cache is None:
            self._recurse = self.result_from
            self._clear = lambda: None
        else:
            self._recurse = cache(self.result_from)
            self._clear = self._recurse.cache_clear


    def result_from(self, node):
        return self._combine(self._visit(self._recurse, node))


    def clear_cache(self):
        self._clear()


    def __call__(self, node):
        return self._recurse(node)


def _getter(func, attr, item, attrgetter, itemgetter, names, tag):
    if (func, attr, item).count(None) != 2:
        name_labels = ', '.join(f'`{name}`' for name in names)
        requirement = 'exactly one of' if required else 'at most one of'
        raise ValueError(f'{requirement} {{{name_labels}}} {tag}')
    if attr is not None:
        func = attrgetter(attr)
    elif item is not None:
        func = itemgetter(item)
    return func


def make_traverser(
    combine, *,
    cache=cache, order=None,
    get_value=None, value_attr=None, value_item=None,
    get_children=None, child_attr=None, child_item=None
):
    get_children = _getter(
        get_children, child_attr, child_item,
        operator.attrgetter, operator.itemgetter,
        ('get_children', 'child_attr', 'child_item'),
        'must be specified and not None'
    )
    if not callable(get_children):
        raise ValueError(
            f'`get_children` (or computed value) must be callable'
        )
    if isinstance(combine, str):
        combine = get_combiner(combine)
    elif not callable(combine):
        raise TypeError(''.join(
            '`combine` must be a lookup string or a callable accepting',
            'a node and a tuple of child results'
        ))
    get_value = _getter(
        get_value, value_attr, value_item,
        # TODO: let the `combine` func modify default value-getting.
        operator.attrgetter, operator.itemgetter,
        ('get_value', 'value_attr', 'value_item'),
        'must be specified and not None'
    )
    visit = get_visitor(get_value, get_children, order)
    return Traverser(visit, combine, cache)
