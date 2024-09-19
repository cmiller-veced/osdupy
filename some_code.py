import json
from collections import defaultdict
from pprint import pprint

import httpx
import pytest
import jsonref
import jsonschema
from jsonschema import validate
from jsonschema import (
    Draft7Validator,
    FormatChecker,
)

from tools import (
    raw_swagger, 
    pet_swagger_local, 
    nws_openapi_local,
    namespacify,
 )



class local:
    class swagger:
        nws = nws_openapi_local
        pet = pet_swagger_local
    class api_base:
        pet = 'https://petstore.swagger.io/v2'
        nws = 'https://api.weather.gov'


# TODO: change name   NO
# TODO: pass schema instead of validator?
def validate_examples(validator, good_ones, bad_ones):    # NWS
    for thing in good_ones:
        assert validator.is_valid(thing)
    for thing in bad_ones:
        assert not validator.is_valid(thing)


def get_component_schemas_nws():    # NWS
  try:
    rs = raw_swagger(local.swagger.nws)
    with_refs = jsonref.loads(json.dumps(rs))
    components = with_refs['components']
    for key in ['responses', 'headers', 'securitySchemes']:
        components.pop(key)
    parameters = components['parameters']
    foo = {key: parameters[key]['schema'] for key in parameters}
    components['parameters'] = foo
    return components
  finally:
    globals().update(locals())


def validation_practice():    # NWS
  try:
    components = get_component_schemas_nws()
    parameters = components['parameters']
    schemas = components['schemas']
    aa = parameters['AlertArea']
#     msg = f'''
#     components.schemas N == {len(cs_keys)}
#     components.parameters N == {len(cprs_keys)}
#     components.parameters - components.schemas N == {len(fu)}
#     '''
#     print(msg)

    # Now for some actual validation.
    validator = Draft7Validator(parameters['AlertZone'], format_checker=FormatChecker())
    # zones.
    # Note: incompatible with area, point, region, region_type.
    good_ones = [[], ['COC123'], ['COZ123']]
    bad_ones = ['' ,['CO'] ,['CO123'] ,'' ]
    validate_examples(validator, good_ones, bad_ones)

    rc = schemas['RegionCode']
    al = schemas['Alert']

    assert schemas['Time'] == parameters['Time']

    vt = Draft7Validator(schemas['Time'], format_checker=FormatChecker())
    vt.schema = schemas['Time']
    good_ones = ['0000', '1955', '2359']
    bad_ones = ['2400', '2500', '09', '1111111', 'x']
    validate_examples(vt, good_ones, bad_ones)

    vd = Draft7Validator(schemas['Date'], format_checker=FormatChecker())
    good_ones = ['2000-01-01']
    bad_ones = ['1999', 'x', 1999, 1111111, 99]
    validate_examples(vd, good_ones, bad_ones)

    vp = Draft7Validator(schemas['Point'], format_checker=FormatChecker())
    vp.schema = schemas['Point']     # ugh.  complex

    vz = Draft7Validator(schemas['Zone'], format_checker=FormatChecker())
    vz.schema = schemas['Zone']
    good_ones = [{}, dict(timeZone=['MT'])]
    bad_ones = ['', 
                dict(foo=1)  # because additionalProperties is False
                ]
    validate_examples(vz, good_ones, bad_ones)

    return schemas
  finally:
    globals().update(locals())


def get_endpoint_schemas_pets():   # petstore
  try:
    schemas = {}
    rs = raw_swagger(local.swagger.pet)
    with_refs = jsonref.loads(json.dumps(rs))
    paths = list(with_refs['paths'].keys())
    for path in paths:
        print(path)
        path_info = with_refs['paths'][path]
        schemas[path] = {}
        for verb in list(path_info.keys()):
            print(f'  {verb}')
            verb_info = path_info[verb]
            params = verb_info['parameters']
            for param_info in params:
                schema = param_info['schema'] if 'schema' in param_info else param_info
                schemas[path][verb] = dict(schema)
    return schemas
  finally:
    globals().update(locals())


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


def validator_for(endpoint, verb):     # pets
    schema = get_endpoint_schemas_pets()[endpoint][verb]
    if 'required' in schema and schema['required'] is True:  # preprocessing
        del schema['required'] 
    fun = lambda ob: validate(ob, schema=schema)
    fun.endpoint = endpoint
    fun.verb = verb
    fun.schema = schema
    return fun


# Call an http(s) API #
# ######################################################################## #


def nws_calls():
  try:
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with httpx.Client(base_url=local.api_base.nws) as client:
        ep = '/alerts'
        ep = '/alerts/active'
        info = rs['paths'][ep]
        assert len(info) == 1
        info = rs['paths'][ep]['get']
        pinfo = rs['paths'][ep]['get']['parameters']

        r = client.get(ep)
        assert r.status_code == 200
        foo = r.json()
        assert type(foo) is dict
        # OK.  There is a successful GET request.
        for key in foo:
            print(key, len(str(foo[key])))
        features = foo['features']
        print(len(features))
        for feat in features:
            fprops = feat['properties']
            ns = namespacify(fprops)
            assert type(fprops) is dict
            head = fprops['headline']
#            print(head)
            zones = fprops['affectedZones']
            # eg ['https://api.weather.gov/zones/county/FLC027']
            # forecast/PZZ475']
            # forecast/PKZ001']
            # county/COC001']
            print(zones)
        print('------------------------')
        for key in feat:
            print(key, len(str(feat[key])))
        # OK.  
        # That was a successful GET request with NO parameters.
        # Sends back a complex json doc.
        #
        # Now do the same but with parameters.
        #
        # OK.   Here goes.
        params = {'AlertArea': 'PK'}      # AlertArea not recognized
        params = {'AlertZone': 'PK'}      # AlertZone not recognized
        params = {'area': 'KS'}
        params = {'area': 'PK'}
        params = {'area': 'CO'}
        r = client.get(ep, params=params)
        foo = r.json()
        assert r.status_code == 200
        # OK.  That was a successful GET request WITH parameters.
        # TODO: cleanup.
        # This has all been super quick & dirty but now we have successful NWS
        # call with parameters.
        # Much more to learn about the API but the basic work is done.

  finally:
    globals().update(locals())


def petstore_calls():
  try:
    with httpx.Client(base_url=local.api_base.pet) as client:
        ep = '/pet/findByStatus'

        vd = validator_for(ep, 'get')
        params = ['available', 'sold']  # passes validation but returns []
        vd(params)
#        a job for preprocessing ?

        r = client.get(ep, params=params)
        assert r.status_code == 200
        foo = r.json()
        assert foo == []
        # OK.  There is a successful GET request.

        params = {'status': 'available'}  # good result but fails validation
        r = client.get(ep, params=params)
        foo = r.json()
        assert len(foo) > 11
        with pytest.raises(jsonschema.exceptions.ValidationError):
            vd(params)

        ep = '/pet'
        params = {"name": 'kittyX', 'photoUrls': [], 'category': {}, 'status': 'sold'}
        header = {'Content-Type': 'application/json'}
        vd2 = validator_for(ep, 'post')
        vd2(params)
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
        vd3 = validator_for(ep, 'post')
        vd3(user_data)
        headers = {'Content-Type': 'application/json'}
        r3 = client.post(ep, data=json.dumps(user_data), headers=headers)
        assert r3.status_code == 200
        assert r3.reason_phrase == 'OK'
        # OK.  Another successful POST request.
 
  finally:
    globals().update(locals())

