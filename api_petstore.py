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
)
from some_code import schema_trans

pet_swagger_local = '~/local/petstore/swagger.json'

#good_schema = with_refs['definitions']['Pet']  # The behavior we want

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


def test_all():
    validate_jsonschema_with_refs()



header = {'accept: application/json'}
petstore_api_base = 'https://petstore.swagger.io/v2'
ep = '/pet/findByStatus'
url = petstore_api_base + ep
params = {'status': 'available'}

rp = httpx.get(url, params=params)  # 
assert rp.status_code == 200

def f():
    request = httpx.Request("GET", "https://example.com")
    with httpx.Client() as client:
        response = client.send(request)


# 
###########################################
from copy import deepcopy
from pprint import pprint
from tools import recur
from tools import delete_key


# schema fetching
def get_definition_schemas_petstore():
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    defs = with_refs['definitions']
    assert list(defs) == ['ApiResponse', 'Category', 'Pet', 'Tag', 'Order', 'User']
    return defs
    # The Pet schema is a good one.
    # What a Pet object should conform to.

# AHA!    brainwave!!! 
# Distinguish two distinct sorts of things to validate.
# endpoint schema
# parameter schema
# An endpoint schema describes one or more parameters

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




def endpoint_schema(endpoint):
    return
def parameter_schema(parameter):
    return

# TODO: and then we have multiple sources of schemas.
# definitions section
# and then the indidguial endponts

def parameter_list_to_schema(parameter_list):
  try:
    d = {}
    for pdict in parameter_list:
        td = {}
        if 'type' in pdict:
            td['type'] = pdict['type']
        if 'format' in pdict:
            td['format'] = pdict['format']
        d[pdict['name']] = td
    d['type'] = 'object'
    d['required'] = [pd['name'] for pd in parameter_list if pd['required']]
    return d
  finally:
    globals().update(locals())
def test_parameter_list_to_schema():
  try:
    s = parameter_list_to_schema(es['parameters'])
    validator = Draft7Validator(s, format_checker=FormatChecker())
    x = {
        'petId': 1234,
    }
    assert validator.is_valid(x)

  finally:
    globals().update(locals())



def get_parameter_schemas():
    return

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
    if 'parameters' in s and len(s['parameters']) > 1:
        s = parameter_list_to_schema(s['parameters'])
    if 'parameters' in s and len(s['parameters']) == 1:
        s = s['parameters'][0]
    return s


def test_endpoint_schema_validation():
    """Here is the way to test validation.
    """
    jdoc = get_schemas()['paths']
    for endpoint in jdoc:
        for verb in jdoc[endpoint]:
            es = endpoint_schema(endpoint, verb)
            print(endpoint, verb)
            print(es)
            print()
            validator = Draft7Validator(es, format_checker=FormatChecker())
            samples = test_parameters[endpoint][verb]
            for thing in samples['good']:
                assert validator.is_valid(thing)
            for thing in samples['bad']:
                assert not validator.is_valid(thing)


# TODO: MVD   minimum viable demonstration
# TODO: MVD   minimum viable demonstration
# TODO: MVD   minimum viable demonstration
# TODO: diff between two json docs.
# TODO: MVI   minimum viable implementation
# TODO: MVI   minimum viable implementation


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
def schema_trans(vinfo): pass
def schema_trans(vinfo, verb):
  try:
    ins = defaultdict(set)
    in_locations = 'body path formData query header'.split()   # data re swagger
    for d in vinfo:   # tmp
        ins[d['in']].add(d['name'])
        assert d['in'] in in_locations
        assert 'in' in d
#        assert 'schema' in d
    if verb == 'post':
        assert all(d['in']=='body' for d in vinfo) or True
    assert all(d['in'] in in_locations for d in vinfo)
    # Not super informative but reveals some data relevant to swagger/etc.

    print('   ', len(vinfo))
    print('   ', dict(ins))
    from pprint import pprint
#    pprint(vinfo)
    print()

    return
  finally:
    globals().update(locals())

def petstore_validator(endpoint, verb):
  try:
    """Return a function to validata parameters for `endpoint`.
    """
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    jdoc = with_refs['paths'][endpoint][verb]
    vinfo = jdoc['parameters']
    schema = schema_trans(vinfo, verb)
    return schema

    is_valid = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)
    return is_valid
  finally:
    globals().update(locals())

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

# TODO: note petstore is the only current api with multiple verbs per endpoint.
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

#            is_valid = petstore_validator(endpoint, verb)
#            schema = is_valid
        continue
        break

        thing = is_valid
        print(endpoint, list(thing))
        continue
  finally:
    globals().update(locals())
# I am a data concierge
# I am a data concierge
# I am a data concierge
# I am a data concierge

def petstore_validate_and_call():
  try:
    rs = raw_swagger(local.swagger.petstore)       # 
    with httpx.Client(base_url=local.api_base.petstore) as client:   # 
        for endpoint in endpoint_names(rs):
            if endpoint not in test_parameters:
                continue
            things = test_parameters[endpoint]
            for verb in things:
                print(endpoint, verb)
                for params in things[verb]['good']:
                    print('  good .............', params)
                for params in things[verb]['bad']:
                    print('  bad .............', params)

                # TODO: insert params approbriately here.
                # destinations...
                #   header
                #   body
                #   query
                #   path
                #   ??
                # There is a lot involved here.
                # Need to figure out where everything goes.

            continue

            for verb in things:
                print(endpoint, verb)
                ep = insert_endpoint_params(ep, sample_query_params)
                print('   calling .............', ep)
                for params in things['good']:
                    assert is_valid(params)
                    print('   ok good valid', params)
                    r = client.get(ep, params=params, headers=head)
                    assert r.status_code == 200
                    # /proteins endpoint return XML!!!!
                    # Until we pass the right header.
                    rj = r.json()
                for params in things['bad']:
                    assert is_valid(params)  # TODO: fix
                    print('   grrr bad but VALID', params)
                    r = client.get(ep, params=params)
                    assert r.status_code != 404    # Bad endpoint
                    assert r.status_code in [400, 500]    # Bad Parameter
  finally:
    globals().update(locals())


def petstore_validate_and_call1():
  try:
    with httpx.Client(base_url=local.api_base.petstore) as client:   # 
        for endpoint in endpoint_names(rs):
            ep = endpoint
            ep0 = ep
            if ep in test_parameters:
                things = test_parameters[ep]
                ep = insert_endpoint_params(ep, sample_query_params)
                # TODO: there is more to do than just insert_endpoint_params.
                # The petstore has a good variety of things.
                # parameters need to be inserted in
                # headers
                # url
                #     path
                #     query
                # body
                # fornData ?????? == body ?????
                if ep0 != ep:
                    print('   calling .............', ep)
                for params in things['good']:
                    assert is_valid(params)
                    print('   ok good valid', params)
                    r = client.get(ep, params=params, headers=head)
                    assert r.status_code == 200
                    # /proteins endpoint return XML!!!!
                    # Until we pass the right header.
                    rj = r.json()
                    if 'proteom' not in ep:
                        if r.text:
                            good_result = r.json()
                            if good_result and type(good_result) is list:
                                good_result = good_result[0]
                            if not good_result:
                                L = 0
                            else:
                                L = good_result['sequence']['length']
                for params in things['bad']:
                    assert is_valid(params)  # TODO: fix
                    assert is_valid(params)  # TODO: fix
                    assert is_valid(params)  # TODO: fix
                    print('   grrr bad but VALID', params)
                    r = client.get(ep, params=params)
                    assert r.status_code != 404    # Bad endpoint
                    assert r.status_code in [400, 500]    # Bad Parameter
                    # or Server Error
                    # 500 from /zones/forecast/{zoneId}/stations
                    # with {'limit': '100'}
  finally:
    globals().update(locals())


pr_faq = """
This system makes it easy for intelligent persons, familiar with the API to
create a representation of the API in Python and perform all the actions of the
API, as described in the OpenAPI file.

Why not use DAO?
How to get started?


"""


# NOT specific to NWS except for base_url
def nws_call(endpoint, params=None):
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(endpoint, params=params)
        assert r.status_code == 200
    return r.json()


