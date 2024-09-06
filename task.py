


def f(dct, lst_or_str):
    """
    >>> nested_data = dict(a=dict(b=dict(c=1)))
    >>> assert nested_data == {'a': {'b': {'c': 1}}}

    Make it conform to either (or both) of the below...

    >>> assert f(nested_data, 'a b c') == 1
    >>> assert f(nested_data, ['a', 'b', 'c']) == 1

    >>> assert f(nested_data, ['a', 'b']) == {'c': 1}
    """
    return 'the right thing'


def non_empty_items_in(lst):
    """
    >>> assert non_empty_items_in(['', ' ', '  ', 1]) == [1]
    """
    # implementation here







