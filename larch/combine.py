import functools, operator


def reducer(binop):
    return functools.partial(functools.reduce, binop)


_combiners = {
    name: combiner
    for combiner, *names in (
        (sum, '+', 'sum'),
        (reducer(operator.concat), 'concat'),
        (reducer(operator.mul), '*', 'product'),
        (reducer(operator.matmul), '@', 'mproduct'),
        # Subtraction and division don't make a lot of sense.
        (reducer(operator.and_), '&', 'and'),
        (reducer(operator.or_), '|', 'or'),
        (reducer(operator.xor), '^', 'xor'),
        (all, 'all'), (any, 'any'), (min, 'min'), (max, 'max')
    )
    for name in names
}


_combiners.update({
    
})


def get_combiner(name):
    return _combiners[name]
