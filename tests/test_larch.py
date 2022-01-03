from larch import __version__, make_traverser, cache, unique_cache


# Data structures etc. for testing purposes
class Graph:
    def __init__(self, name, value, *children):
        self._name = name
        self._value = value
        self._children = list(children)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @property
    def children(self):
        return self._children
        # Clients may modify the list, but not replace it.


    def __str__(self):
        return self._name


    __repr__ = __str__


D, E, F = Graph('D', 4), Graph('E', 5), Graph('F', 6)
B, C = Graph('B', 2, D, E), Graph('C', 3, E, F)
DAG = Graph('A', 1, B, C)
E2 = Graph('E', 5)
C2 = Graph('C', 3, E2, F)
Tree = Graph('A', 1, B, C2)


# Tests.
def test_version():
    assert __version__ == '0.1.0'


def test_dag():
    assert make_traverser(
        'sum_preorder', child_attr='children', value_attr='value',
        cache=None
    )(DAG) == 26
    assert make_traverser(
        'sum_preorder', child_attr='children', value_attr='value'
    )(DAG) == 26
    assert make_traverser(
        'sum_preorder', child_attr='children', value_attr='value',
        cache=unique_cache()
    )(DAG) == 21


def test_tree():
    assert make_traverser(
        'sum_preorder', child_attr='children', get_value=str,
        cache=None
    )(Tree) == 'ABDECEF'
    assert make_traverser(
        'sum_preorder', child_attr='children', get_value=str
    )(Tree) == 'ABDECEF'
    # Since we're looking at a tree with no joins, the cache doesn't matter.
    assert make_traverser(
        'sum_preorder', child_attr='children', get_value=str,
        cache=unique_cache('')
    )(Tree) == 'ABDECEF'
