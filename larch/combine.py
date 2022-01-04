import functools, operator


_combiners = {
    'sum': functools.partial(functools.reduce, operator.add),
}


def get_combiner(name):
    return _combiners[name]
