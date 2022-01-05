import functools, operator


def reducer(binop):
    return functools.partial(functools.reduce, binop)


def _tuple_flatten(children):
    return tuple(i for child in children for i in child)


def _list_flatten(children):
    return [i for child in children for i in child]


_combiners = {
    name: combiner
    for combiner, *names in (
        # Mathematical combinations.
        # Subtraction and division don't make a lot of sense generally.
        # Where they're needed, they can be recast as sums/products by
        # using negation and reciprocation judiciously.
        (sum, '+', 'sum'),
        (reducer(operator.mul), '*', 'product'),
        (reducer(operator.matmul), '@', 'matrix-product'),
        # Bitwise / set operations.
        (reducer(operator.and_), '&', 'and', 'intersection'),
        (reducer(operator.or_), '|', 'or', 'union'),
        (reducer(operator.xor), '^', 'xor', 'symmetric-difference'),
        # Make flat lists/tuples.
        (reducer(operator.concat), '()', '[]', 'concat'),
        # roughly equivalent to &/|, but using logical rather than
        # bitwise operators allows the leaf types to be non-boolean.
        (all, 'all'), (any, 'any'),
        # min and max, OTOH, are numeric.
        (min, 'min'), (max, 'max'),
        # Build nested structures.
        # Python doesn't support nested sets, as sets aren't hashable.
        (tuple, '(())', 'nested-tuple'),
        (list, '[[]]', 'nested-list'),
    )
    for name in names
}


def get_combiner(name):
    return _combiners[name]
