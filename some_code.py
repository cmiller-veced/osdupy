import json

import jsonref
import jsonschema
from jsonschema import validate
import httpx
import pytest

from tools import (raw_swagger, pet_swagger_local, )



# Test #
# ######################################################################## #
    

# fooeey.
# Should be using the version without refs.
# That way I will know when I'm getting reuse.
def use_it():
  # getting familiar with the swagger.

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


    jdoc = rs
    jdoc = with_refs
    for ep in jdoc['paths']:
        path_info = deep_key('paths '+ep, jdoc)
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
                    assert param["in"] == 'body'
                    msg = ''
                else:
                    foo = param
                    msg = '-'*22 + ' ' + param["in"]
                print(f'    {param["name"]}  {msg}')
                if has_schema:
                    if 'properties' in s:
                        props = s['properties']
                    else:
                        assert s['type'] == 'array'
                        props = s['items']['properties']
                        print(f'      -------array of----')
                        sap = s
                    for prop in props:
                        print(f'      {prop}')

  finally:
    globals().update(locals())


def use_it2():
  try:
    """Mucking around in the swagger to make sense of it.
    """
    validators = {}
    rs = raw_swagger(pet_swagger_local)
    with_refs = jsonref.loads(json.dumps(rs))
    jdoc = with_refs
    jdoc = rs
    for ep in jdoc['paths']:
        path_info = deep_key('paths '+ep, jdoc)
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
                    assert param["in"] == 'body'
                    msg = ''
                else:
                    foo = param
                    msg = '-'*22 + ' ' + param["in"]
                print(f'    {param["name"]}  {msg}')
                if has_schema:
                    msg = f'--schema--   {s}'
                    try:
                        defn = s['$ref']
                    except KeyError:
                        defn = s['items']['$ref']
                    defn = defn.split('/')[-1]
                    sc2 = jdoc['definitions'][defn]
                    # OK.
                    # Here we have extracted the correct schema.
                    # Now validate data using the schema.
                    # So return a validator or whatever.
                    vfun = lambda ob: validate(instance=ob, schema=sc2)
                    vfun.name = defn
                    validators[defn] = vfun
                    # OK.
                    # Here are a bunch of validators. !!!!!!!!!!!!
                    # Slick
                else:
                    msg = f'--param--   {param}'
                    xx = param
                    if 'required' in param:
                        param.pop('required')
                    vfun = lambda ob: validate(instance=ob, schema=param)
                    vfun.name = param['name']
                    validators[param['name']] = vfun
                    # TODO: for each endpoint, have an associated validator.
                    # and associated validator for the return value.
                print(f'    {msg}')
                print()
                # validation
                # serialization
                # what was the other buzzword???????
 
  finally:
    globals().update(locals())


def get_endpoints():
  try:
    """
    """
    n = 0
    validators = {}
    rs = raw_swagger(pet_swagger_local)
    with_refs = jsonref.loads(json.dumps(rs))
    paths = list(rs['paths'].keys())
    for path in paths:
        path_info = rs['paths'][path]
        validators[path] = {}
        for verb in list(path_info.keys()):
            verb_info = path_info[verb]
            validators[path][verb] = []
            params = verb_info['parameters']
            i = 0
            for param_info in params:
                has_schema = 'schema' in param_info
                has_ref = has_schema and  '$ref' in param_info['schema'] or ''
                assert has_ref in [True, False, '']
                vinfo = [param_info['name']]
                if has_ref:
                    v = with_refs['paths'][path][verb]['parameters'][i]
                    s = with_refs['paths'][path][verb]['parameters'][i]['schema']
                    vinfo.append(s)
                    n += 1
#                    assert len(s) in [2, 3]
                print(path, verb, has_schema, has_ref)
                validators[path][verb].append(vinfo)
                i += 1
  finally:
    ffff = 1      # why is it at a different level?????????
    s1 = validators['/pet']['post'][0][1]
    s2 = validators['/pet']['put'][0][1]
    s3 = validators['/store/order']['post'][0][1]
#    s3['additionalProperties'] = False   # TODO: move to preprocessing step.

    s4 = validators['/user']['post'][0][1]
    s5 = validators['/user/{username}']['put'][ffff][1]

    assert s4 == s5
    assert s1 == s2
    del s5
    del s2
    # Now have 3 schemas; 1,3, 4.
#    for s in (s1, s3, s4): s['additionalProperties'] = False
    v1 = lambda ob: validate(instance=ob, schema=s1)
    v3 = lambda ob: validate(instance=ob, schema=s3)
    v4 = lambda ob: validate(instance=ob, schema=s4)

    good_ones = [
        (v1, {'name': 'luna', 'photoUrls':[]}),
        (v3, {'foo': 1}),   # because additional keys not disabled)
        (v3, {'quantity': 1, 'status': 'placed'}),
        (v3, {'quantity': 1}),
        (v4, {}),
    ]
    bad_ones = [
        (v1, {'name': 1, 'photoUrls':[]}),
        (v3, {'quantity': 'x'}),
        (v4, 'x'),
    ]
    for (v, arg) in good_ones:
        v(arg)
    for (v, arg) in bad_ones:
        with pytest.raises(jsonschema.exceptions.ValidationError):
            v(arg)

#    [[the_name], sc] = validators['/user/{username}']['put']
#    ll = len(sc)
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


