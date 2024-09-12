import json

import jsonref
import jsonschema
from jsonschema import validate
import httpx
import pytest

from tools import (raw_swagger, pet_swagger_local, )


# Test #
# ######################################################################## #


def use_it2():
  try:
    """Mucking around in the swagger to make sense of it.
    """
    validators = {}    # bad name
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
                # cvs
                # conversion
 
  finally:
    globals().update(locals())


def get_endpoints():
  try:
    n = 0
    schemas = {}
    rs = raw_swagger(pet_swagger_local)
    with_refs = jsonref.loads(json.dumps(rs))
    paths = list(rs['paths'].keys())
    for path in paths:
        path_info = rs['paths'][path]
        schemas[path] = {}
        for verb in list(path_info.keys()):
            verb_info = path_info[verb]
            schemas[path][verb] = []
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
                if not has_schema:
                    vinfo.append(param_info)
                schemas[path][verb].append(vinfo)
                i += 1
  finally:
    ffff = 1      # why is it at a different level?????????
    s1 = schemas['/pet']['post'][0][1]
    s2 = schemas['/pet']['put'][0][1]
    s3 = schemas['/store/order']['post'][0][1]
#    s3['additionalProperties'] = False   # TODO: move to preprocessing step.

    s4 = schemas['/user']['post'][0][1]
    s5 = schemas['/user/{username}']['put'][ffff][1]

    assert s4 == s5
    assert s1 == s2
    del s5
    del s2
    # Now have 3 schemas; 1,3, 4.
#    for s in (s1, s3, s4): s['additionalProperties'] = False
    v1 = lambda ob: validate(instance=ob, schema=s1)
    v3 = lambda ob: validate(instance=ob, schema=s3)
    v4 = lambda ob: validate(instance=ob, schema=s4)
    s3a = s3.copy()
    s3a['additionalProperties'] = False
    v3a = lambda ob: validate(instance=ob, schema=s3a)

    # OK
    # Above covers referred schemas.
    # Now deal with inline schemas.
    [the_name2, sc2] = schemas['/user/{username}']['put'][0]
    [the_name, sc] = schemas['/pet/findByStatus']['get'][0]

    sca = sc.copy()
    vca = lambda ob: validate(instance=ob, schema=sca)
    sc.pop('required')    # preprocessing
    vc = lambda ob: validate(instance=ob, schema=sc)  # reads sc at RUN time.
    vc2 = lambda ob: validate(instance=ob, schema=sc2)
#    sc2.pop('required')    # preprocessing

    good_ones = [
        (v1, {'name': 'luna', 'photoUrls':[]}),
        (v3, {'foo': 1}),   # because additional keys not disabled)
        (v3, {'quantity': 1, 'status': 'placed'}),
        (v3, {'quantity': 1}),
        (v4, {}),
        (vc, ['pending']),
        (vc, []),
        (vc2, 'foobar'),
    ]
    bad_ones = [
        (v1, {'name': 1, 'photoUrls':[]}),
        (v3, {'quantity': 'x'}),
        (v4, 'x'),
        (v3a, {'foo': 1}),   # additional keys disabled
        (vc, {}),
        (vc, 'pending'),
        (vc, ['x']),
        (vc2, []),
    ]
    for (v, arg) in good_ones:
        v(arg)
    for (v, arg) in bad_ones:
        with pytest.raises(jsonschema.exceptions.ValidationError):
            v(arg)



#    [[the_name], sc] = schemas['/user/{username}']['put']
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

