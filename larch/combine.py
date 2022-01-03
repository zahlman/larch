import functools, operator


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


def get_combiner(combine, get_value):
    return _combiners[combine](get_value)
