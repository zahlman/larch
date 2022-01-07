import pytest
from larch import __version__, make_traverser, cache as default_cache, unique_cache
from larch.traversal import TraversalOrder


# Data structures etc. for testing purposes
class GraphNode:
    def __init__(self, value, *children):
        # `value` is a plain attribute. We thus test access for both
        # ordinary attributes and properties (not that there's any *reason*
        # to expect one to fail where the other succeeds...)
        self.value = value
        self._children = list(children)


    @property
    def children(self):
        return self._children
        # Clients may modify the list, but not replace it.


def _numeric_dag():
    # A simple directed, acyclic graph with one join.
    # Numeric node values so that we can test e.g. summing the values.
    D, E, F = GraphNode(4), GraphNode(5), GraphNode(6)
    B, C = GraphNode(2, D, E), GraphNode(3, E, F)
    return GraphNode(1, B, C)


def _build_tree(values):
    A, B, C, D, E, F, G = map(GraphNode, values)
    B.children.extend([A, C])
    F.children.extend([E, G])
    D.children.extend([B, F])
    return D


def _alpha_tree():
    # A simple, full binary tree with nodes A to G inclusive.
    # Inorder traversal gives letters in order.
    return _build_tree('ABCDEFG')


def _numeric_tree():
    # A simple, full binary tree with integer values 0 to 6 inclusive.
    # Inorder traversal gives values in order.
    return _build_tree(range(7))


class _matrix11:
    # Trivial matrix type for testing __matmul__.
    def __init__(self, data):
        self._data = data


    def __matmul__(self, other):
        return _matrix11(self._data * other._data)
        

def _mat_tree():
    # Like the numeric tree, just to test the `@` combiner is accessible.
    # Also shows multiplication without zero values.
    return _build_tree(map(_matrix11, range(1, 8)))


def _set_tree():
    elements = 'ABCDEF'
    return _build_tree(set(elements[:i]) for i in range(7))


# Tests.
def test_version():
    assert __version__ == '0.1.0+25'


@pytest.mark.parametrize("cache,result", [
    (None, 26), (default_cache, 26), (unique_cache(), 21)
])
def test_dag_caches(cache, result):
    DAG = _numeric_dag()
    assert make_traverser(
        'sum', order='pre', child_attr='children', value_attr='value',
        cache=cache
    )(DAG) == result 


@pytest.mark.parametrize("cache", [None, default_cache, unique_cache('')])
def test_tree_caches(cache):
    Tree = _alpha_tree()
    # Since we're looking at a tree with no joins, the result doesn't vary. 
    assert make_traverser(
        'concat', order='pre', child_attr='children', value_attr='value',
        cache=cache
    )(Tree) == 'DBACFEG'


@pytest.mark.parametrize("order,result", [
    # Specify via the enum type.
    (TraversalOrder.PRE, 'DBACFEG'),
    # Specify via strings.
    ('in', 'ABCDEFG'),
    # String names for orders are case insensitive.
    ('pOsT', 'ACBEGFD'),
    # Specify 2 values on the left - equivalent to postorder here.
    (2, 'ACBEGFD'),
    # Leaves only.
    (None, 'ACEG')
])
def test_good_tree_orders(order, result):
    Tree = _alpha_tree()
    assert make_traverser(
        'concat', order=order, child_attr='children', value_attr='value'
    )(Tree) == result
    
    
@pytest.mark.parametrize("order", [0.5, 'bad', ()])
def test_bad_tree_orders(order):
    # Invalid orderings.
    with pytest.raises(ValueError):
        make_traverser(
            'concat', order=order, child_attr='children', value_attr='value'
        )


@pytest.mark.parametrize("operation,result", [
    ('+', 21), ('*', 0), ('&', 0), ('|', 7), ('^', 7),
    ('all', False), ('any', True), ('min', 0), ('max', 6)
])
def test_numeric_ops(operation, result):
    Tree = _numeric_tree()
    assert make_traverser(
        operation, order='in', child_attr='children', value_attr='value'
    )(Tree) == result


def test_matmul():
    Tree = _mat_tree()
    assert make_traverser(
        '@', order='in', child_attr='children', value_attr='value'
    )(Tree)._data == 5040


@pytest.mark.parametrize("operation,result", [
    ('[[]]', [[['A'], 'B', ['C']], 'D', [['E'], 'F', ['G']]]),
    ('(())', ((('A',), 'B', ('C',)), 'D', (('E',), 'F', ('G',))))
])
def test_nesting(operation, result):
    Tree = _alpha_tree()
    assert make_traverser(
        operation, order='in', child_attr='children', value_attr='value'
    )(Tree) == result


@pytest.mark.parametrize("operation,result", [
    ('intersection', set()), ('union', {'A', 'B', 'C', 'D', 'E', 'F'}),
    ('symmetric-difference', {'B', 'D', 'F'}),
    ('all', False), ('any', True),
    ('min', set()), ('max', {'A', 'B', 'C', 'D', 'E', 'F'})
])
def test_set_ops(operation, result):
    Tree = _set_tree()
    assert make_traverser(
        operation, order='in', child_attr='children', value_attr='value'
    )(Tree) == result
