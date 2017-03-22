from itertools import zip_longest


def grouper(n, iterable):
    """Split an *iterable* in groups of *n*. Last group may be shorter."""
    args = [iter(iterable)] * n
    return ([e for e in t if e is not None] for t in zip_longest(*args))

