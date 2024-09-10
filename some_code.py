import json
import os
from functools import singledispatch  # for heterogeneous recursive data structure
from types import SimpleNamespace


import jsonref
import jsonschema
from jsonschema import validate
import httpx


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
    

def use_it():
  try:
    pe = deep_key('paths /pet', with_refs)
    pns = namespacify(pe)
    assert len(pns.post.parameters) == 1
    [pram] = pns.post.parameters
    wtf = """
    >>> pram.in
      File "<stdin>", line 1
        pram.in
             ^
    SyntaxError: invalid syntax
    """      # what's the problem?
    ps = pram.schema
    globals().update(locals())


    for ep in with_refs['paths']:
        path_info = deep_key('paths '+ep, with_refs)
        path_ns = namespacify(path_info)
        print(ep)
        for verb in path_info:
            verb_info = path_info[verb]
            verb_ns = namespacify(verb_info)
            params = verb_info['parameters']
#            print(f'  {verb}', len(params), type(params))
            print(f'  {verb}')
            for param in params:
                pns = namespacify(param)
                has_schema = 'schema' in param
                if has_schema:
                    s = param['schema']
                    nss = namespacify(s)
                else:
                    foo = param
                if has_schema:
                    assert param["in"] == 'body'
                    msg = ''
                else:
                    msg = param["in"]
                print(f'    {param["name"]}  {msg}')
                if has_schema:
                    if 'properties' in s:
                        for prop in s['properties']:
                            print(f'      {prop}')
                    else:
                        sa = s
                        assert s['type'] == 'array'
                        print(f'      ' + 'x'*44)

  finally:
    globals().update(locals())



def test_deep_key():
    rs = raw_swagger(pet_swagger_local)
    assert deep_key('definitions Category', rs) == rs['definitions']['Category']
    assert deep_key(['definitions', 'Category'], rs) == rs['definitions']['Category']




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
# TODO: find some complexity metrics
# LOC and McCabe are both good.
# I'd like a version of McCabe that accounts for 3rd party libs.
# or something like that.


def namespacify(thing):
    ugly_hack = json.dumps(thing, indent=1)
#    ugly_hack = json.dumps(thing)   # when ugly_hack is no longer needed we
#    will use this line instead.
    return json.loads(ugly_hack, object_hook=lambda d: SimpleNamespace(**d))
    # ugly_hack:    indent=1
    # ugly_hack is required, and works because ...
    # By the way, this specific problem (with json.dumps) can be bypassed by passing any of the "special" parameters dumps accepts (e.g indent, ensure_ascii, ...) because they prevent dumps from using the JSON encoder implemented in C (which doesn't support dict subclasses such as rpyc.core.netref.builtins.dict). Instead it falls back to the JSONEncoder class in Python, which handles dict subclasses.
    # https://github.com/tomerfiliba-org/rpyc/issues/393


def test_namespace():    # dict => namespace
  try:
    rs = raw_swagger(pet_swagger_local)
    ns0 = namespacify(rs)

    with_refs = jsonref.loads(json.dumps(rs))
    ns = namespacify(with_refs)     # ugly_hack required for this 

    assert ns0.definitions.Pet.properties.category == namespacify(rs['definitions']['Pet']['properties']['category'])

    assert ns.definitions.Pet.properties.category == namespacify(with_refs['definitions']['Pet']['properties']['category'])
    assert ns.definitions.Pet.properties.category == namespacify(deep_key('definitions Pet properties category', with_refs))

    # convert namespace back to dict.
    v0 = vars(ns)  # ok but not recursive

    # recursively convert namespace back to dict.
    v = json.loads(json.dumps(ns, default=lambda s: vars(s)))

  finally:
    globals().update(locals())



# Call an http(s) API #
# ######################################################################## #


def petstore_calls():
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


# bring it all together
# ######################################################################## #
# I believe that is all the big pieces.
#

