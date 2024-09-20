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
    local,
    namespacify,
    endpoint_names,
 )


# TODO: change name   NO
# TODO: pass schema instead of validator?
def validate_examples(validator, good_ones, bad_ones):    # NWS
    for thing in good_ones:
        assert validator.is_valid(thing)
    for thing in bad_ones:
        assert not validator.is_valid(thing)


def validation_practice_nws():    # NWS
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


def nws_education():
  try:
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with_refs = jsonref.loads(json.dumps(rs))

    stationId = 'KRCM'    # OK
    stationId = 'CO100'   # OK
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
  finally:
    globals().update(locals())


def nws_series():
  try:
    """ Get a series of observations suitable for putting in a pandas DF,
    and then a jupyter notebook.
    """
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with_refs = jsonref.loads(json.dumps(rs))
    ep = '/stations/{stationId}/observations'
    
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
    # params = ['start': 'date-time', 'end': '2024-09-21...'}
    # '2024-09-13T18:39:00+00:00'

    zinfo = rs['paths'][ep]['get']['parameters']
    yinfo = with_refs['paths'][ep]['get']['parameters']
    xinfo1 = [{'name': 'start', 'in': 'query', 'description': 'Start time', 'schema': {'type': 'string', 'format': 'date-time'}}, {'name': 'end', 'in': 'query', 'description': 'End time', 'schema': {'type': 'string', 'format': 'date-time'}}, {'name': 'limit', 'in': 'query', 'description': 'Limit', 'schema': {'maximum': 500, 'minimum': 1, 'type': 'integer'}}]
    assert yinfo == xinfo1
    xinfo = {
        'start': {'type': 'string', 'format': 'date-time'}, 
        'end': {'type': 'string', 'format': 'date-time'}, 
      'limit': {'maximum': 500, 'minimum': 1, 'type': 'integer'}}
    # TODO: auto-extract schema.
    xinfo = dict(properties=xinfo)
    validator = Draft7Validator(xinfo, format_checker=FormatChecker())
    assert validator.is_valid(params)

    stationId = 'CO100'   # OK
    stationId = 'KRCM'    # OK
    ep = '/stations/{stationId}/observations'
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(ep, params=params)
        assert r.status_code == 200

        final = []
        feats = r.json()['features']
        for ft in feats: 
            pt = ft['properties']
            for key in [ '@id', '@type', 'elevation', 'station', 'rawMessage', 'icon', 'presentWeather', 'cloudLayers', 'textDescription', ]:
                pt.pop(key)
            for key in pt:
                if type(pt[key]) is dict:
                    pt[key] = pt[key]['value']
            print(pt)
            final.append(pt)

        df = pandas.DataFrame(final)
        assert df.shape == (50, 15)
        temps = df.temperature
        # TODO:   work to do on auto-validation.

  finally:
    globals().update(locals())


def nws_calls():
  try:
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with_refs = jsonref.loads(json.dumps(rs))
    with httpx.Client(base_url=local.api_base.nws) as client:

        ep = '/alerts'
        ep = '/alerts/active'

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

# TODO: how to get good stationId ???
