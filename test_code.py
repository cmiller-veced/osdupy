import pytest

from some_code import validator_for


def endpoint_good_data():
    d = defaultdict(lambda:{})
    d['/pet']['post'] = [
        {'name': 'luna', 'photoUrls':[]},
        {'name': 'dulci', 'photoUrls':[]},
    ]
    d['/pet/findByStatus']['get'] = [
        ['available'],
        ['available', 'pending'],
        [],
    ]
    d['/pet/findByTags']['get'] = [
        ['foo'],
        ['foo', 'bar'],
        [],
    ]
    d['/pet/{petId}']['get'] = [
        99,
    ]
    d['/store/order']['post'] = [
        {'foo': 1},   # because additional keys not disabled)
        {'quantity': 1, 'status': 'placed'},
        {'quantity': 1},
    ]
    d['/user']['post'] = [
        {},
        {'username': 'foo'},
    ]
    return d

 
def endpoint_bad_data():
    d = defaultdict(lambda:{})
    d['/pet']['post'] = [
        {'name': 11, 'photoUrls':[]},
        {'name': 1, 'photoUrls':[]},
    ]
    d['/pet/findByStatus']['get'] = [
        ['x'],
    ]
    d['/pet/findByTags']['get'] = [
        [{}],
        {},
    ]
    d['/pet/{petId}']['get'] = [
        9.9,
        '9',
        {}
    ]
    d['/store/order']['post'] = [
        {'quantity': 'x'},
    ]
    d['/user']['post'] = [
        {'username': 9},
    ]
    return d
 

def test_endpoint_validators():
  try:
    datas = [
        (True, endpoint_good_data()),
        (False, endpoint_bad_data())
    ]
    for (is_good_data, data) in datas:
        print('-'*55, is_good_data)
        for endpoint in data:
            print(endpoint)
            for verb in data[endpoint]:
                print(f'  {verb}')
                v = validator_for(endpoint, verb)
                for thing in data[endpoint][verb]:
                    if is_good_data:
                        v(thing)
                        print(f'    {thing}   ok')
                    else:
                        with pytest.raises(jsonschema.exceptions.ValidationError):
                            v(thing)
                        print(f'    {thing}   ok')
  finally:
    globals().update(locals())





# validation
# serialization
# what was the other buzzword???????
# cvs
# conversion

# Test #
# ######################################################################## #

def test_endpoint_schemas():
    schemas = get_endpoint_schemas()


