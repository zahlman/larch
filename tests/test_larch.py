from larch import __version__, make_traverser, cache, unique_cache


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


def _alpha_tree():
    # A simple, full binary tree with nodes A to G inclusive.
    # Inorder traversal gives letters in order.
    A, C, E, G = GraphNode('A'), GraphNode('C'), GraphNode('E'), GraphNode('G')
    B, F = GraphNode('B', A, C), GraphNode('F', E, G)
    return GraphNode('D', B, F)


# Tests.
def test_version():
    assert __version__ == '0.1.0'


def test_dag_caches():
    DAG = _numeric_dag()
    assert make_traverser(
        'sum', order='pre', child_attr='children', value_attr='value',
        cache=None
    )(DAG) == 26
    assert make_traverser(
        'sum', order='pre', child_attr='children', value_attr='value'
    )(DAG) == 26
    assert make_traverser(
        'sum', order='pre', child_attr='children', value_attr='value',
        cache=unique_cache()
    )(DAG) == 21


def test_tree_caches():
    Tree = _alpha_tree()
    assert make_traverser(
        'concat', order='pre', child_attr='children', value_attr='value',
        cache=None
    )(Tree) == 'DBACFEG'
    assert make_traverser(
        'concat', order='pre', child_attr='children', value_attr='value'
    )(Tree) == 'DBACFEG'
    # Since we're looking at a tree with no joins, the cache doesn't matter.
    assert make_traverser(
        'concat', order='pre', child_attr='children', value_attr='value',
        cache=unique_cache('')
    )(Tree) == 'DBACFEG'
