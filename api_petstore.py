from collections import defaultdict
from test_data_petstore import test_parameters
import json

import httpx
import jsonref
import jsonschema
from jsonschema import ( Draft7Validator, FormatChecker, validate)

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    endpoint_names,
    insert_endpoint_params,
    recur, delete_key, DotDict, namespacify,
)
#from some_code import schema_trans

from copy import deepcopy
from pprint import pprint
from demo_class import validated_for_dict
import types
from types import SimpleNamespace
import pytest

header = {'accept: application/json'}
sample_data = {
    'username': 'merlin', 
    'file': 'foofile', 
    'api_key': 'foobar', 
    'additionalMetadata': 'foof', 
    'name': 'yourName', 
#    'status': 'sold', 
    'status': ['sold'], 
    'password': 'xxxxx', 
    'petId': 99, 
    'orderId': 9, 
    'tags': ['foo']
}


# schema fetching
def get_definition_schemas_petstore():
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    defs = with_refs['definitions']
    assert list(defs) == ['ApiResponse', 'Category', 'Pet', 'Tag', 'Order', 'User']
    return defs
    # The Pet schema is a good one.
    # What a Pet object should conform to.


def get_endpoint_locations():
    # by subtracting
    rs = raw_swagger(local.swagger.petstore)       # 
    top_level_keys = 'swagger info host basePath tags schemes securityDefinitions externalDocs definitions'.split()
    ep_keys = 'summary description operationId consumes produces responses security'.split()
    param_keys = 'required schema type deprecated'.split()
    schema_keys = 'format maximum minimum items collectionFormat'.split()
    all_keys = top_level_keys + ep_keys + param_keys + schema_keys
    for key in all_keys:
        delete_key(rs, key)
    return rs

def test_endpoint_locations():
  try:
    jdoc = get_endpoint_locations()['paths']
    for path in jdoc:
        for verb in jdoc[path]:
            assert len(jdoc[path][verb]) == 1
            assert 'parameters' in jdoc[path][verb]
            for param in jdoc[path][verb]['parameters']:
                assert len(param) == 2
                assert sorted(list(param)) == ['in', 'name']
  finally:
    globals().update(locals())


def get_schemas():
    # by subtracting
    rs = raw_swagger(local.swagger.petstore)       # 
    with_refs = jsonref.loads(json.dumps(rs))
    rs = with_refs
    top_level_keys = 'swagger info host basePath tags schemes securityDefinitions externalDocs'.split()
    ep_keys = 'operationId consumes produces responses security'.split()
    param_keys = []
    schema_keys = ['xml']
    all_keys = top_level_keys + ep_keys + param_keys  + schema_keys
    for key in all_keys:
        delete_key(rs, key)
    return rs
def test_get_schemas():
  try:
    jdoc = get_schemas()    #['paths']
    assert sorted(list(jdoc)) == ['definitions', 'paths']
    jd = jdoc['definitions']
    jp = jdoc['paths']
    assert list(jd) == ['ApiResponse', 'Category', 'Pet', 'Tag', 'Order', 'User']
    assert list(jp) == ['/pet/{petId}/uploadImage', '/pet', '/pet/findByStatus', '/pet/findByTags', '/pet/{petId}', '/store/inventory', '/store/order', '/store/order/{orderId}', '/user/createWithList', '/user/{username}', '/user/login', '/user/logout', '/user/createWithArray', '/user']
  finally:
    globals().update(locals())


def parameter_list_to_schema(parameter_list):
    d = {}
    for pdict in parameter_list:
        td = {}
        if 'type' in pdict:
            td['type'] = pdict['type']
        if 'format' in pdict:
            td['format'] = pdict['format']
        if 'in' in pdict:
            td['in'] = pdict['in']
        d[pdict['name']] = td
    d['type'] = 'object'
    d['required'] = [pd['name'] for pd in parameter_list if pd['required']]
    return d


def test_parameter_list_to_schema():
    s = parameter_list_to_schema(es['parameters'])
    validator = Draft7Validator(s, format_checker=FormatChecker())
    x = { 'petId': 1234, }
    assert validator.is_valid(x)


#def get_parameter_schemas(): return

# working
if 1:      # insert info into request
    interface_schema = dict(
        type='object',
        additionalProperties=False,
        #    required = ['httpx_request', 'endpoint_info'],
        required = ['endpoint_info'],
        properties=dict(
            #        httpx_request=dict( type='string',),
            # Here we have a shortcoming of jsonschema.
            # I want to specify that httpx_request must be httpx.Request object but
            # there's no way to do that in jsonschema.
            # TODO: maybe sometime, redo this validator in Pydantic so we can
            # specify httpx.Request.
            # But otoh, if something else ever gets passed in it will be really easy
            # to track down.
            httpx_request=dict(),
            endpoint_info=dict(
                required = ['endpoint', 'verb'],
                type='object',
                endpoint=dict( type='string',),
                verb=dict( type='string',),
                ),
            parameters=dict(
                type='object',
                body=dict( type='object',),
                headers=dict( type='object',),
                path=dict( type='object',),
                query=dict( type='array',),
            )
        )
    )


    class Combined(validated_for_dict(interface_schema)):
        def insert_to_request(self, httpx_request: httpx.Request):
            """
            """
            request = httpx_request
            parameters = self['parameters']
            info = self['endpoint_info']
            # TODO: put them together.
            return 'xxx'
     
    dx = dict(parameters=dict(query=[]), httpx_request='foof')  # OK
    dx = dict(
        parameters=dict(query=[]), 
        httpx_request=[],
        endpoint_info=dict(
            endpoint='/foo/bar/{bat}',
            verb='post',
        ),
    )  # OK
    dbad = dict(params=dict(query=[]))  # OK
    ##############
    ##############
    ok = Combined(dx)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        db = Combined(dbad)
    okns = json.loads(json.dumps(ok), object_hook=DotDict)
    assert okns.parameters == {'query': []}
    assert okns.parameters.query == []
    assert okns.endpoint_info.verb == 'post'
    with pytest.raises(KeyError):
        ick = okns.insert_to_request()
    ick = ok.insert_to_request('req')


# schema fetching
def endpoint_schema(endpoint, verb):
    """Pull schema with some adjustments for internal inconsistency within the
    OpenAPI doc.
    AFII: adjust for internal inconsistency
    """
    jdoc = get_schemas()['paths']
    defs = get_schemas()['definitions']
    for ep in jdoc:
        for v in jdoc[ep]:
            if (endpoint, verb) == (ep, v):
                s = jdoc[endpoint][verb]

                # AFII
                if len(s['parameters']) == 1:
                    p = s['parameters'][0]
                    if p['in'] == 'body':
                        assert 'schema' in p
                        s = p['schema']
    # AFII
    if 'parameters' in s:
        if len(s['parameters']) > 1:
            s = parameter_list_to_schema(s['parameters'])
            print('yoohoo')
            print('yoohoo')
            print('yoohoo')
        elif len(s['parameters']) == 1:
            s = s['parameters'][0]
    return s


# working
def test_endpoint_schema_validation():
  try:
    """
    """
    jdoc = get_schemas()['paths']
    for endpoint in jdoc:
        for verb in jdoc[endpoint]:
            es = endpoint_schema(endpoint, verb)
            print(endpoint, verb)
            print(es)
            validator = Draft7Validator(es, format_checker=FormatChecker())
            samples = test_parameters[endpoint][verb]
            for thing in samples['good']:
                assert validator.is_valid(thing)
                if thing:
                    gthing = thing
            for thing in samples['bad']: 
                assert not validator.is_valid(thing)
            # TODO: call the endpoint with the params
            # need other info from swagger.
            other_info = endpoint_info(endpoint, verb)
            di = dict(
                endpoint_info=dict(endpoint=endpoint, verb=verb),
                parameters=dict(
                    body={},
                    headers={},
                    path={},
                    query={},
                ),
                #                foo=2,
            )
            c = Combined(di)

            # exp
            if 'properties' in es:
                for prop in es['properties']:
                    assert 'in' not in prop
            if 'in' in es:
                print('x'*66)
                di['parameters'][es['in']] = True
                print(es['in'])
                print('x'*66)
            if verb in ['post', 'put']:
                di['parameters']['body'] = True
            print('   ', di['parameters'])
            print()

            kw = {}
            url = local.api_base.petstore + endpoint
            if di['parameters']['body'] == True:
                kw['data'] = gthing    # give the Request a body

    header = {'Content-Type: application/json'}   # 415 Unsupported Media Type
    header = {'Content-Type': 'application/json'}   # 400 bad input
    userId = 2314345670987
    username = f'user{userId}'
    with httpx.Client() as client:
        if (endpoint, verb) == ('/user', 'post'):
            kd = {'id': userId, 'username': username}
            request = httpx.Request(verb, url, headers=header, json=kd)   # 200 OK
            response = client.send(request)
        verb = 'get'
        endpoint = f'/user/{username}'
        url = local.api_base.petstore + endpoint
        urequest = httpx.Request(verb, url)
        uresponse = client.send(urequest)   # 200 OK
  finally:
    globals().update(locals())

# goal:  Make it work like this...
def petstore_validate_and_call1():
  try:
    with httpx.Client(base_url=local.api_base.petstore) as client:   # 
        for endpoint in endpoint_names(rs):
            for verb in endpoint:
                for params in test_data['good']:
                    assert params_ok
                    load_params
                    send_params
                    assert it_worked
                for params in test_data['bad']:
                    assert params_NOT_ok
                    load_params
                    send_params
                    assert NOT_it_worked
  finally:
    globals().update(locals())

def endpoint_info(endpoint, verb):
  try:
    """Pull endpoint info relevant for the API call.
    """
    jdoc = get_schemas()['paths']
    for ep in jdoc:
        for v in jdoc[ep]:
            if (endpoint, verb) == (ep, v):
                s = jdoc[endpoint][verb]
  finally:
    globals().update(locals())


def petstore_endpoint_verbs(endpoint):
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    globals().update(locals())
    return list(thing)

def petstore_endpoint_verb_details(endpoint, verb):
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint][verb]
    return thing


# TODO: up until now I have been validating all parameters together.
# BUT.
# often each parameter gets its own schema and so could be validated
# individually.
# Q.  Maybe each param should be validated individually?
# A.  The petstore API shows that parameters definitely need to be inserted
# individually into the right place.  So maybe it makes sense to validate
# individually but maybe not.
# def schema_trans(vinfo): pass
# def schema_trans(vinfo, verb):
#   try:
#     ins = defaultdict(set)
#     in_locations = 'body path formData query header'.split()   # data re swagger
#     for d in vinfo:   # tmp
#         ins[d['in']].add(d['name'])
#         assert d['in'] in in_locations
#         assert 'in' in d
# #        assert 'schema' in d
#     if verb == 'post':
#         assert all(d['in']=='body' for d in vinfo) or True
#     assert all(d['in'] in in_locations for d in vinfo)
#     # Not super informative but reveals some data relevant to swagger/etc.
# 
#     print('   ', len(vinfo))
#     print('   ', dict(ins))
#     from pprint import pprint
# #    pprint(vinfo)
#     print()
# 
#     return
#   finally:
#     globals().update(locals())


# def petstore_validator(endpoint, verb):
#   try:
#     """Return a function to validata parameters for `endpoint`.
#     """
#     rs = raw_swagger(local.swagger.petstore)
#     with_refs = jsonref.loads(json.dumps(rs))
#     thing = with_refs['paths'][endpoint]
#     jdoc = with_refs['paths'][endpoint][verb]
#     vinfo = jdoc['parameters']
#     schema = schema_trans(vinfo, verb)
#     return schema
# 
#     is_valid = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)
#     return is_valid
#   finally:
#     globals().update(locals())


def petstore_investigate_endpoints():
  try:
    schemaless_params = set()
    fu = set()
    # inspect the swagger, carefully.
    rs = raw_swagger(local.swagger.petstore)       # 
    for endpoint in endpoint_names(rs):
        print(endpoint)
        verbs = petstore_endpoint_verbs(endpoint)
        for verb in verbs:
            print('   ', verb)
            details = petstore_endpoint_verb_details(endpoint, verb)
            if 1:
                delete_key(details, 'xml')
                delete_key(details, 'produces')
                delete_key(details, 'consumes')
                delete_key(details, 'summary')
                delete_key(details, 'responses')
                delete_key(details, 'tags')
            for pram in details['parameters']:
                pname = pram['name']
                schema = pram['schema'] if 'schema' in pram else pram
                # compensate for bad info in swagger file...
                if pname == 'status':
                    schema = rs['paths']['/pet/findByStatus']['get']['parameters'][0]
                if pname == 'file':
                    schema['type'] = 'string'
                dv = Draft7Validator(schema, format_checker=FormatChecker())
                sd = sample_data[pname]

                if 'schema' in pram:
                    schema = pram['schema']
                has_schema = True if 'schema' in pram else False
                print(f'      name: {pram["name"]}  in: {pram["in"]}')
                if has_schema:
                    assert pram["in"] == 'body'
#                    print('                   ', list(schema))
                if not has_schema:
                    schemaless_params.add(pname)
                    print('                   ', pram)

                    # compensate for bad info in swagger file...
                    if pname == 'status':
                        pram = rs['paths']['/pet/findByStatus']['get']['parameters'][0]
                    if pname == 'file':
                        pram['type'] = 'string'

                    dv = Draft7Validator(pram, format_checker=FormatChecker())
                    sd = sample_data[pname]
                    try:
                        assert dv.is_valid(sd)
                        flag = 'OK'
                    except:
                        flag = '---------------------------'
                        fu.add(pname)
                        if pname == 'file': return
#                        if pname == 'status': return
                    print('                   ', flag)
        continue
        break

        thing = is_valid
        print(endpoint, list(thing))
        continue
  finally:
    globals().update(locals())



