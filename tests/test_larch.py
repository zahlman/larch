from larch import __version__, Traverser, cache, unique_cache


# Data structures etc. for testing purposes
class Graph:
    def __init__(self, name, value, *children):
        self._name = name
        self._value = value
        self._children = list(children)

    @property
    def value(self):
        print('getting:', self)
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


def add_values(current, from_children):
    return current.value + sum(from_children)


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
    assert Traverser(get_children, add_values, None)(DAG) == 26
    assert Traverser(get_children, add_values, cache)(DAG) == 26
    assert Traverser(get_children, add_values, unique_cache())(DAG) == 21


def test_tree():
    assert Traverser(get_children, add_values, None)(Tree) == 26
    assert Traverser(get_children, add_values, cache)(Tree) == 26
    assert Traverser(get_children, add_values, unique_cache())(Tree) == 26
