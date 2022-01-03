from larch import __version__, Traverser, cache, unique_cache, combine_sum_preorder


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


def get_children(g):
    return g.children


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
    add_values = combine_sum_preorder(lambda g: g.value)
    assert Traverser(get_children, add_values, None)(DAG) == 26
    assert Traverser(get_children, add_values, cache)(DAG) == 26
    assert Traverser(get_children, add_values, unique_cache())(DAG) == 21


def test_tree():
    add_values = combine_sum_preorder(str)
    assert Traverser(get_children, add_values, None)(Tree) == 'ABDECEF' 
    assert Traverser(get_children, add_values, cache)(Tree) == 'ABDECEF'
    # Since we're looking at a tree with no joins, the cache doesn't matter.
    assert Traverser(get_children, add_values, unique_cache(''))(Tree) == 'ABDECEF'
