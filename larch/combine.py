import functools, operator


def _combine_reduce(max_before, operation, node_value, values):
    # We allow "max_before" in case the operation isn't commutative.
    if max_before is None: # avoid duplicating with slices.
        max_before = len(child_values)
    # insert node value in the appropriate place.
    values = values[:max_before] + (node_value,) + values[max_before:]
    # There is at least one value, so we don't need an initial value.
    return functools.reduce(operation, values)


_combiners = {
    'sum_preorder': functools.partial(_combine_reduce, 0, operator.add),
    'sum_inorder': functools.partial(_combine_reduce, 1, operator.add),
    'sum_postorder': functools.partial(_combine_reduce, None, operator.add)
}


def get_combiner(name):
    return _combiners[name]
