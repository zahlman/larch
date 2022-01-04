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


def _children_only(get_children, recurse, node):
    for child in get_children(node):
        yield recurse(child)


def get_visitor(get_value, get_children, order):
    if get_value is None:
        # no value is generated for the current node when traversing.
        if order is not None:
            raise ValueError(
                "cannot specify order when nodes don't produce a value"
            )
        return functools.partial(_children_only, get_children)
    else:
        try:
            left_count = {
                'in': 1, 'pre': 0, 'post': None
            }[order]
        except KeyError:
            raise ValueError(
                '`order` must be specified as `in`, `pre` or `post` ' +
                'when nodes produce a value'
            )
        return functools.partial(_visitor, get_children, get_value, left_count)
