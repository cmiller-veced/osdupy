import json
import os
from functools import singledispatch  # for heterogeneous recursive data structure

import jsonref
import jsonschema
from jsonschema import validate


pet_swagger = 'https://petstore.swagger.io/v2/swagger.json'
pet_swagger_local = '~/local/petstore/swagger.json'


def raw_swagger(at_path):
    with open(os.path.expanduser(at_path)) as fh:
        return json.load(fh)


# Validation using jsonschema #
# ######################################################################## #

def validate_jsonschema_with_refs():
    good_ones = [
        {"name": 'kittyX', 'photoUrls': []},
        {"name": 'kittyX', 'photoUrls': [], 'category': {}},
        {"name": 'kittyX', 'photoUrls': [], 'status': 'sold'},
        {"name": 'kittyX', 'photoUrls': [], 'category': {}, 'status': 'sold'},
    ]
    bad_ones = [
        {},
        {"name": 'kittyX'},
        {"name": 'kittyX', 'photoUrls': [], 'category': ''}, 
        {"name": 'kittyX', 'photoUrls': [], 'status': ''},
    ]
    rs = raw_swagger(pet_swagger_local)
    with_refs = jsonref.loads(json.dumps(rs))
    good_schema = with_refs['definitions']['Pet']  # The behavior we want
    bad_schemas = [{}, dict(foo=2)]   # jsonschema allows any dict to be a schema.

    for ob in good_ones:
        validate(instance=ob, schema=good_schema)
        print('ok good', ob)

    for ob in bad_ones:
        try:
            validate(instance=ob, schema=good_schema)
        except jsonschema.exceptions.ValidationError:
            print('ok bad', ob)

    for schema in bad_schemas:
        validate(instance={}, schema=schema)
        print('crap!')

    globals().update(locals())




# Working with json data #
# ######################################################################## #


# Recursion over a heterogeneous data structure.
@singledispatch
def recur(arg, indent=0):
    print(f'{" "*indent}{arg}')

@recur.register
def _(arg: list, indent=0):
    for thing in arg:
        recur(thing, indent=indent+1)

@recur.register
def _(arg: dict, indent=0):
    for key in arg:
        recur(key, indent=indent+1)
        recur(arg[key], indent=indent+1)
        print()
# This is good but extremely limited.
# It does the recursion correctly but simply prints out stuff in a totally rigid
# way.


# fetch from deeply nested dicts.
# TODO: add ability to do similar with lists in the mix.
@singledispatch
def deep_key(keys, dct):
    keys.reverse()
    while keys:
        key = keys.pop()
        dct = dct[key]
    return dct

@deep_key.register
def _(keys: str, dct):
    return deep_key(keys.split(), dct)


# Test #
# ######################################################################## #
    

def test_deep_key():
    rs = raw_swagger(pet_swagger_local)
    assert deep_key('definitions Category', rs) == rs['definitions']['Category']


def test_recursion():
  try:
    rs = raw_swagger(pet_swagger_local)
    print(len(str(rs)))
    print(len(rs))
    rs_keys = ['swagger', 'info', 'host', 'basePath', 'tags', 'schemes', 'paths', 'securityDefinitions', 'definitions', 'externalDocs']
    assert sorted(list(rs.keys())) == sorted(rs_keys)
    for key in rs_keys:
        print(key, type(rs[key]))
        print(rs[key])
        print()
    recur(rs)

  finally:
    globals().update(locals())


def test_all():
    test_deep_key()
    test_recursion()
    validate_jsonschema_with_refs()


#test_all()

