import larch


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


def get_value(g):
    return g.value


def add_values(current, from_children):
    print('adding:', current, from_children)
    return current + sum(from_children)


D, E, F = Graph('D', 4), Graph('E', 5), Graph('F', 6)
B, C = Graph('B', 2, D, E), Graph('C', 3, E, F)
A = Graph('A', 1, B, C)


print(
    larch.Traverser(
        get_children, get_value, add_values, None#larch.unique_cache()
    )(A)
)
