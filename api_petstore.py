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


def get_definition_schemas_petstore():
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    defs = with_refs['definitions']
    assert list(defs) == ['ApiResponse', 'Category', 'Pet', 'Tag', 'Order', 'User']
    return defs
    # The Pet schema is a good one.
    # What a Pet object should conform to.


# TODO: MVD   minimum viable demonstration
# TODO: MVD   minimum viable demonstration
# TODO: MVD   minimum viable demonstration
# TODO: MVD   minimum viable demonstration
# TODO: diff between two json docs.


ps = get_definition_schemas_petstore()['Pet']
po = deepcopy(ps)
delete_key(ps, 'xml')



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

status_schema = {'name': 'status', 'in': 'query', 'description': 'Status values that need to be considered for filter', 'required': True, 'type': 'array', 'items': {'type': 'string', 'enum': ['available', 'pending', 'sold'], 'default': 'available'}, 'collectionFormat': 'multi'}




# TODO: note petstore is the only current api with multiple verbs per endpoint.
def petstore_investigate_endpoints():
  try:
    schemaless_params = set()
    fu = set()
    # inspect the swagger, carefully.
    rs = raw_swagger(local.swagger.petstore)       # 
    status_schema = rs['paths']['/pet/findByStatus']['get']['parameters'][0]
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
                    if pname == 'status':
                        pram = status_schema
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


