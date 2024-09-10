import json
import os
from functools import singledispatch  # for heterogeneous recursive data structure

import jsonref
import jsonschema
from jsonschema import validate
import httpx  # giving it a try


pet_swagger = 'https://petstore.swagger.io/v2/swagger.json'
pet_swagger_local = '~/local/petstore/swagger.json'
petstore_api_base = 'https://petstore.swagger.io/v2'


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
# TODO: This is good but extremely limited.
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
# TODO: test the recursion by finding all dict items with key == '4xx'
#   esp 415
# TODO: dict => namespace
# TODO: dict => namespace
# TODO: dict => namespace
# TODO: dict => namespace


# Call an http(s) API #
# ######################################################################## #


def fok():
  try:
    with httpx.Client(base_url=petstore_api_base) as client:
        ep = '/pet/findByStatus'
        params = {'status': 'available'}
        r = client.get(ep, params=params)
        assert r.status_code == 200
        foo = r.json()
        # OK.  There is a successful GET request.

        ep = '/pet'
        params = {"name": 'kittyX', 'photoUrls': [], 'category': {}, 'status': 'sold'}
        header = {'Content-Type': 'application/json'}
        r2 = client.post(ep, data=json.dumps(params), headers=header)
        assert r2.status_code == 200
        assert r2.reason_phrase == 'OK'
        # OK.  There is a successful POST request.

        ep = '/user'
        user_data = {
          "id": 0,
          "username": "string",
          "firstName": "string",
          "lastName": "string",
          "email": "string",
          "password": "string",
          "phone": "string",
          "userStatus": 0
        }
        headers = {'Content-Type': 'application/json'}
        r3 = client.post(ep, data=json.dumps(user_data), headers=headers)
        assert r3.status_code == 200
        assert r3.reason_phrase == 'OK'
        # OK.  another successful POST request.
 
  finally:
    globals().update(locals())

