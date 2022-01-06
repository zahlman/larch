from enum import IntEnum
import functools


def _visitor(get_children, get_value, left_count, recurse, node):
    yielded_node = False
    for i, child in enumerate(get_children(node)):
        if i == left_count:
            yield get_value(node)
            yielded_node = True
        yield recurse(child)
    if not yielded_node:
        yield get_value(node)


def _children_only(get_children, get_value, recurse, node):
    is_leaf = True
    for child in get_children(node):
        is_leaf = False
        yield recurse(child)
    if is_leaf:
        yield get_value(node)


class TraversalOrder(IntEnum):
    # Specifies the order of traversal, in terms of the maximum number of
    # children to visit before the current node.
    IN = 1
    PRE = 0
    POST = -1 # i.e. infinite, since it will never be equal.


def get_visitor(get_value, get_children, order):
    # Make sure of this in a previous step.
    assert get_value is not None
    if order is None:
        return functools.partial(_children_only, get_children, get_value)
    if isinstance(order, str):
        try:
            order = TraversalOrder[order.upper()]
        except KeyError:
            pass # still a string, failing the next check
    if not isinstance(order, int):
        raise ValueError(
            "`order` must be `None`, an integer, or an order name string " +
            "(`'in'`, `'pre'` or `'post'`, not case sensitive)"
        )
    return functools.partial(_visitor, get_children, get_value, order)
