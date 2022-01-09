# The Larch.

## Overview

`larch` helps avoid boilerplate when writing graph (but mostly tree) traversal algorithms, by separating the concern of traversal from the concern of what to do at each node. This can be thought of as a general implementation of the Visitor design pattern.

See the tests for example usage. The main interface is:

    def make_traverser(
        combine, *,
        cache=cache, order=None,
        get_value=None, value_attr=None, value_item=None,
        get_children=None, child_attr=None, child_item=None
    ):

where

`combine` -> a function that accepts results from child nodes and possibly a value for the current node, and computes a result for the current node. It should take one argument, which is a sequence of child-results with the current value inserted at the appropriate point.

`combine` can also instead be a string, which will be looked up as
follows:

* `'sum'`, `'product'`, `'matrix-product'` (or `'+'`, `'*'`, `'@'`) - apply the specified numeric operation to the values.

* `'and'`, `'or'`, `'xor'` (or `'&'`, `'|'`, `'^'`) - combine boolean values with that logic.

* `'intersection'`, `'union'`, `'symmetric-difference'` (or `'&'`, `'|'`, `'^'`) - combine sets with that logic.

* `'concat'`, `'()'`, `'[]'` - accumulate flat sequences of results. The `get_value` function must return a singleton sequence of the appropriate type.

* `'nested-tuple'`, `'nested-list'` (or `'(())'`, `'[[]]'`) - create nested lists or tuples that reflect the tree structure.

* `'all'`, `'any'`, `'min'`, `'max'` - apply the corresponding builtin functions. (Of course, you could also specify them directly.) Note that `any` and `all` will short-circuit and avoid traversing the rest of the tree where possible.

* `cache` -> a decorator that implements a memoization cache (or None). By default, the standard library `functools` implementation is used. You can also explicitly disable this with `cache=None`, or use `larch.unique_cache` to specify a dummy value used when a node is encountered again. (This is useful for, for example, summing the node values in a DAG.)

* `order` -> the order of traversal. This can be:

* `None` -> the traversal will not yield values for internal nodes at all.

* an `int` specifying the maximum number of children to visit before the current node. If negative, all children will be visited first.

* `'pre'` or `larch.traversal.TraversalOrder.PRE` - equivalent to `0`; does a pre-order traversal.

* `'in'` or `larch.traversal.TraversalOrder.IN` - equivalent to `1`; does an in-order traversal for binary trees. (To represent binary trees that can have a single child that is "on the right", use some kind of proxy for the left child.)

* `'post'` or `larch.traversal.TraversalOrder.PRE` - equivalent to `-1`; does a post-order traversal.

`'get_value'` -> a function that accepts a node and returns its "value" as appropriate for the traversal. Alternately, `'value_attr'` can be the (string) name of an attribute to look for on each node and use as the value; or `'value_item'` similarly for a dict item or element index (or slice; that is, anything that could be passed to the node's `__getitem__`).

`'get_value'` -> a function that accepts a node and returns an iterable of child nodes. Alternately, `'child_attr'` can be the (string) name of an attribute of the node which stores its children; or `'child_item'` similarly for a dict item or element index (or slice; that is, anything that could be passed to the node's `__getitem__`).

----

`larch` can also be used to implement recursive algorithms, by treating the call tree as a virtual tree. Suppose we want to replace a recursive function that accepts several position arguments. The strategy is to represent a node as a sequence of arguments for a recursive call; use the `get_value` callback to return the value for base cases; use `get_children` to return the argument-sequences that would be needed for recursive calls.

See the tests for example usage.

## TODO

* Proper documentation
* Stack-based traversal to avoid running into recursion limits (need to think about how to make this work without disabling short-circuiting of the `combine` operation)
* Proper detection of joins and cycles (rather than using a cache hack that ruins long-term caching)
* Ability to handle joins and cycles differently (by either ignoring them, returning a dummy value or raising an exception)
* Ability to use dynamic programming techniques directly (filling the cache iteratively) rather than leaning on memoization; and to use optimized, Numpy-based caches for this