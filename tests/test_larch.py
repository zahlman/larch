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


def _chain(n):
    # test deep linear recursion.
    start = GraphNode(1)
    current = start
    for i in range(2, n+1):
        current.children.append(GraphNode(i))
        current = current.children[-1]
    return start, current 


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


# Need completely new architecture for this.
@pytest.mark.xfail
def test_stack():
    start, end = _chain(2000)
    assert make_traverser(
        '+', order='post', child_attr='children', value_attr='value'
    )(start) == 2000


# Make this easier to use and avoid the sentinel.
def test_cycle():
    start, end = _chain(10)
    end.children.append(start)
    start = start.children[0].children[0].children[0]
    assert make_traverser(
        '[]', order='pre', child_attr='children',
        get_value = lambda node: [node.value],
        cache=unique_cache([])
    )(start) == [4,5,6,7,8,9,10,1,2,3] 


# Examples of "virtual nodes" used for recursive algorithms.
def test_fib():
    assert make_traverser(
        '+', 
        get_children = lambda n: range(n)[-2:],
        get_value = lambda n: 1
    )(10) == 89


def test_pascal():
    def smaller(x, y):
        if x > 0:
            yield (x-1, y)
        if y > 0:
            yield (x, y-1)
    assert make_traverser(
        '+',
        get_children = lambda xy: smaller(*xy),
        get_value = lambda xy: 1
    )((5, 5)) == 252
