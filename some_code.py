import json
from pprint import pprint

import jsonref
import jsonschema
from jsonschema import validate
import httpx
import pytest

from tools import (raw_swagger, pet_swagger_local, )


def get_endpoint_schemas():
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
#                print(path, verb, has_schema, has_ref)
                if not has_schema:
                    vinfo.append(param_info)
                schemas[path][verb].append(vinfo)
                i += 1
    for endpoint in schemas:
        for verb in schemas[endpoint]:
            schema = schemas[endpoint][verb]
            try:
                schema = schema[0][1] if schema else None
            except IndexError:
                schema = None
            if schema is not None:
                schema = dict(schema)
                assert type(schema) is dict
            schemas[endpoint][verb] = schema
    return schemas


def preprocess_schemas(schemas):
    """
    Preprocessing can have multiple steps because of multiple problem sources.
    - type errors by the swagger author.  eg swagger says int but should be str.
    - things we just want to change in the schema, eg additionalProperties.
    - shortcomings of jsonschema,  eg date formats?
    """
    return schemas
#    s3['additionalProperties'] = False   # TODO: move to preprocessing step.


def endpoint_names(swagger_doc):
    return list(swagger_doc['paths'].keys())


def endpoint_good_data():
    d = {}
    d['/pet'] = {}
    d['/pet']['post'] = [
        {'name': 'luna', 'photoUrls':[]},
        {'name': 'dulci', 'photoUrls':[]},
    ]
    d['/store/order'] = {}
    d['/store/order']['post'] = [
        {'foo': 1},   # because additional keys not disabled)
        {'quantity': 1, 'status': 'placed'},
        {'quantity': 1},
    ]
    d['/user'] = {}
    d['/user']['post'] = [
        {},
    ]

    return d
    good_ones = [
        (vc, ['pending']),
        (vc, []),
        (vc2, 'foobar'),
    ]
 
def endpoint_bad_data():
    d = {}
    d['/pet'] = {}
    d['/pet']['post'] = [
        {'name': 11, 'photoUrls':[]},
        {'name': 1, 'photoUrls':[]},  # Should fail.  Shows it's not working !
    ]
    d['/store/order'] = {}
    d['/store/order']['post'] = [
        {'quantity': 'x'},
    ]
 
    return d
    bad_ones = [
        (v4, 'x'),
        (v3a, {'foo': 1}),   # additional keys disabled
        (vc, {}),
        (vc, 'pending'),
        (vc, ['x']),
        (vc2, []),
    ]
 

def test_endpoint_validators():
  try:
    print('-'*55 + ' good data')
    data = endpoint_good_data()
    for endpoint in data:
        print(endpoint)
        for verb in data[endpoint]:
            print(f'  {verb}')
            v = validator_for(endpoint, verb)
            for thing in data[endpoint][verb]:
                v(thing)
                print(f'    {thing}   ok')

    print()
    print('-'*55 + ' bad data')
    data = endpoint_bad_data()
    for endpoint in data:
        print(endpoint)
        for verb in data[endpoint]:
            print(f'  {verb}')
            v = validator_for(endpoint, verb)
            for thing in data[endpoint][verb]:
                with pytest.raises(jsonschema.exceptions.ValidationError):
                    v(thing)
                print(f'    {thing}   ok')
  finally:
    globals().update(locals())


def validator_for(endpoint, verb):
    schema = get_endpoint_schemas()[endpoint][verb]
    return lambda ob: validate(ob, schema=schema)


def test_endpoint_schemas():
    schemas = get_endpoint_schemas()


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
    pass
#    globals().update(locals())


# validation
# serialization
# what was the other buzzword???????
# cvs
# conversion

# Test #
# ######################################################################## #


