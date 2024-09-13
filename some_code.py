import json
from collections import defaultdict
from pprint import pprint

import jsonref
import jsonschema
from jsonschema import validate
import httpx

from tools import (raw_swagger, pet_swagger_local, petstore_api_base,
 )

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
    s3['additionalProperties'] = False   # TODO: move to preprocessing step.
    """
    return schemas


def endpoint_names(swagger_doc):
    return list(swagger_doc['paths'].keys())


def validator_for(endpoint, verb):
    schema = get_endpoint_schemas()[endpoint][verb]
    if 'required' in schema and schema['required'] is True:  # preprocessing
        del schema['required'] 
    fun = lambda ob: validate(ob, schema=schema)
    fun.endpoint = endpoint
    fun.verb = verb
    fun.schema = schema
    return fun


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
        validate = validator_for(ep, 'post')
        validate(user_data)
        headers = {'Content-Type': 'application/json'}
        r3 = client.post(ep, data=json.dumps(user_data), headers=headers)
        assert r3.status_code == 200
        assert r3.reason_phrase == 'OK'
        # OK.  another successful POST request.
 
  finally:
    globals().update(locals())

