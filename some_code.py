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
import pandas          

from tools import (
    raw_swagger, 
    pet_swagger_local, 
    nws_openapi_local,
    namespacify,
 )


class local:       # our data.   (vs their data (in swagger))
    class swagger:
        pet = pet_swagger_local
        nws = nws_openapi_local
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



# Call an http(s) API #
# ######################################################################## #


def nws_calls():
  try:
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with_refs = jsonref.loads(json.dumps(rs))
    with httpx.Client(base_url=local.api_base.nws) as client:

        ep = '/alerts'
        ep = '/alerts/active'

        learning_about_parameters = True
        learning_about_parameters = False

        if learning_about_parameters:
            # Learning about the parameters
            ep = '/stations/{stationId}/observations'

            info = rs['paths'][ep]
            assert len(info) in [1, 2]
            info = rs['paths'][ep]['get']

            pinfo = rs['paths'][ep]['get']['parameters']
            xinfo = with_refs['paths'][ep]['get']['parameters']
#            ainfo = xinfo[4]
#            einfo = xinfo[2]
            for param in xinfo:   # list
                binfo = param
                pname = binfo['name']
                assert binfo['in'] == 'query'
                if 'style' in binfo:
                    assert binfo['style'] == 'form'
                    # `point` does not have style.
                    # and has inline schema.
                if 'explode' in binfo:
                    assert binfo['explode'] in [True, False]
                print(pname)
            return

        no_parameters = False

        if no_parameters:
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


        with_parameters = True
        with_parameters = False
        if with_parameters:    # GET request with parameters.

            params = {'AlertArea': 'PK'}      # AlertArea not recognized
            params = {'AlertZone': 'PK'}      # AlertZone not recognized
            params = {'area': 'KS'}
            params = {'area': 'PK'}
            params = {'area': 'CO'}
            params = {'area': ['CO']}
            # https://www.weather.gov/nwr/eventcodes
            params = {
                'area': ['CO'],
                'event': ['Winter Weather Advisory'],
                #            'event': ['Freeze Warning'],  No such event ????
                }
            r = client.get(ep, params=params)
            foo = r.json()
            assert r.status_code == 200
            # OK.  That was a successful GET request WITH parameters.
            # TODO: cleanup.
            # This has all been super quick & dirty but now we have successful NWS
            # call with parameters.
            # Much more to learn about the API but the basic work is done.
            feats = foo['features']
            for feat in feats:
                feature_properties = feat['properties']
                feature_event = feat['properties']['event']

        params = {}
        more_alerts = True
        more_alerts = False
        if more_alerts:
            ep = '/alerts/active/count'
            r = client.get(ep, params=params)
            count = r.json()
            assert r.status_code == 200
            # Shows region, area and zone names

            ep = '/alerts/active/zone/'
            zone = 'forecast/COZ082'    # NO
            zone = 'COZ082'    # Pikes Peak
            ep = f'/alerts/active/zone/{zone}'
            r = client.get(ep, params=params)
            pp = r.json()
            assert r.status_code == 200

            ep = f'/alerts/types'
            r = client.get(ep, params=params)
            ets = r.json()['eventTypes']
            assert r.status_code == 200

        glossary = True
        glossary = False
        if glossary:
            ep = '/glossary'
            r = client.get(ep, params=params)
            things = r.json()['glossary']
            for gthing in things:
                print(gthing['term'])
            assert r.status_code == 200

        icons = True
        icons = False
        if icons:
            ep = '/icons'
            r = client.get(ep, params=params)
            things = r.json()['icons']
            for ithing in things:
                print(ithing)
            assert r.status_code == 200

        params = {'area': 'CO'}   # bad parameter.  Find station parameters.
        sinfo = rs['paths']['/stations']['get']['parameters']
        params = {'state': 'CO'}   # 
        stations = True
        stations = False
        if stations:
            ep = '/stations'
            r = client.get(ep, params=params)
            rj = r.json()
            names = r.json()['observationStations']
            things = r.json()['features']
            for sthing in things: 
                print(sthing)
            assert r.status_code == 200
            nom = names[-1]
            station = things[-1]
            # 'stationIdentifier': 'COOPCOS'
            # Colorado Springs Municipal Airport
            # Other interesting info in sthing.


        params = {}
        observations = True
        observations = False
        if observations:
            stationId = 'COOPCOS'   # Not Found
            stationId = 'KRCM'    # OK
            stationId = 'CO100'   # OK
            ep = f'/stations/{stationId}/observations/latest'
            r = client.get(ep, params=params)
            props = r.json()['properties']
            for othing in props:
                print(othing)
            temp = props['temperature']
            assert r.status_code == 200


          # start here
          # start here
          # start here
          # start here
          # start here
          # start here
        # Get a series of observations suitable for putting in a pandas DF,
        # and then a jupyter notebook.
        params = {}
        params = {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   '100',     # works OK at the endpoint but fails validation
        }
        params = {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   501,    # fails validation as it should
        }
        params = {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   50,
        }

        # TODO: validate the parameters.
        xinfo = with_refs['paths'][ep]   #['get']['parameters']
        xinfo = with_refs['paths'][ep]['get']   #['parameters']

        # fails here vvv because ^^^ is a list.
#        xinfo = with_refs['paths'][ep]['get']['parameters']
        xinfo = [{'name': 'start', 'in': 'query', 'description': 'Start time', 'schema': {'type': 'string', 'format': 'date-time'}}, {'name': 'end', 'in': 'query', 'description': 'End time', 'schema': {'type': 'string', 'format': 'date-time'}}, {'name': 'limit', 'in': 'query', 'description': 'Limit', 'schema': {'maximum': 500, 'minimum': 1, 'type': 'integer'}}]
        xinfo = {
            'start': {'type': 'string', 'format': 'date-time'}, 
            'end': {'type': 'string', 'format': 'date-time'}, 
          'limit': {'maximum': 500, 'minimum': 1, 'type': 'integer'}}
        xinfo = dict(properties=xinfo)
        validator = Draft7Validator(xinfo, format_checker=FormatChecker())
        assert validator.is_valid(params)

        series = False
        series = True
        if series:
            stationId = 'KRCM'    # OK
            stationId = 'CO100'   # OK
            ep = f'/stations/{stationId}/observations'
            r = client.get(ep, params=params)

            final = []
            feats = r.json()['features']
            for ft in feats: 
                pt = ft['properties']
                for key in [
                '@id',
                '@type',
                'elevation',
                'station',
                'rawMessage',
                'icon',
                'presentWeather',
                'cloudLayers',
                'textDescription',
                ]:
                    pt.pop(key)
                for key in pt:
                    if type(pt[key]) is dict:
                        pt[key] = pt[key]['value']
                print(pt)
                final.append(pt)
#            temp = props['temperature']
            assert r.status_code == 200
          # That's it!!!
          # `final` is ready to be a pandas DF.
          # start here
          # start here
          # start here
          # start here
          # start here
          # Pass and validate parameters.
          # Which will be start and/or end times.
#          params = ['start': 'date-time', 'end': '2024-09-21...'}
          # '2024-09-13T18:39:00+00:00'
        df = pandas.DataFrame(final)
        # super !!!!!!!!!!
        # Now need tons of cleanup


        products = True
        products = False
        if products:
            ep = '/products'
            r = client.get(ep, params=params)
            context = r.json()['@context']
            things = r.json()['@graph']
            for pthing in things: 
                print(pthing)
            assert r.status_code == 200





  finally:
    globals().update(locals())
# TODO: pagination
# TODO: pagination
# TODO: pagination

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


def validator_for(endpoint, verb):     # pets
    schema = get_endpoint_schemas_pets()[endpoint][verb]
    if 'required' in schema and schema['required'] is True:  # preprocessing
        del schema['required'] 
    fun = lambda ob: validate(ob, schema=schema)
    fun.endpoint = endpoint
    fun.verb = verb
    fun.schema = schema
    return fun


