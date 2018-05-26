import common_util


def doctest_iterate_dict():
    """
    # iterate dict w/ key, value
    >>> d = {'a':1, 'b':2}
    >>> d.items()
    dict_items([('a', 1), ('b', 2)])
    >>> for k, v in d.items():
    ...     print(k, v)
    a 1
    b 2

    # simple for : just get keys
    >>> for e in d:
    ...     print(e)
    a
    b
    """


if __name__ == '__main__':
    common_util.call_funcs(lambda s: s.startswith('test_'))
