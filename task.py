"""
Make life easier when dealing with json data.
"""


def nested_key(lst_or_str, dct):
    """
    >>> nested_data = dict(a=dict(b=dict(c=1)))
    >>> assert nested_data == {'a': {'b': {'c': 1}}}

    Make it conform to either (or both) of the below...

    >>> assert nested_key('a b c', nested_data) == 1
    >>> assert nested_key(['a', 'b', 'c'], nested_data) == 1

    >>> assert nested_key(['a', 'b'], nested_data) == {'c': 1}
    """
    return 'the right thing'


def non_empty_items_in(lst):
    """
    >>> assert non_empty_items_in(['', ' ', '  ', 1]) == [1]
    """
    # implementation here


