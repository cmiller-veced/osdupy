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
from jinja2 import Environment, PackageLoader, select_autoescape

from tools import (
    raw_swagger, 
    local,
    namespacify,
    endpoint_names,
 )
ep1 = '/stations/{stationId}/observations'


def get_component_schemas_nws():    # NWS
    rs = raw_swagger(local.swagger.nws)
    with_refs = jsonref.loads(json.dumps(rs))
    components = with_refs['components']
    for key in ['responses', 'headers', 'securitySchemes']:
        components.pop(key)
    parameters = components['parameters']
    foo = {key: parameters[key]['schema'] for key in parameters}
    components['parameters'] = foo
    return components


def nws_validator(endpoint):
    """Return a function to validata parameters for `endpoint`.
    """
    rs = raw_swagger(local.swagger.nws)                              # global
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    vinfo = thing['parameters'] if 'parameters' in thing else thing['get']['parameters']
    schema = schema_trans(vinfo)     # NWS-specific
    assert list(schema.keys()) == ['properties']
#    print(endpoint, list(schema['properties'].keys()))
    is_valid = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)
    is_valid.endpoint = endpoint
    is_valid.schema = schema
    # TODO: better function name
    return is_valid


def nws_validate_data():
    for ep in endpoint_names(rs):
        is_valid = nws_validator(ep)
        print(ep)
        if ep in test_parameters:
            things = test_parameters[ep]
            for params in things['good']:
                assert is_valid(params)
                print('   ok good', params)
            for params in things['bad']:
                assert not is_valid(params)
                print('   ok bad', params)

query_params = {
    'productId': 'ppppp',
    'typeId': 'tttttt',
    'zoneId': 'WYZ432',
    'stationId': 'CO100',
    'locationId': 'llllll',
}

"""
    # Insert stationId into endpoint path
    stationId = ''   # OK
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(templatified(ep1))
    ep = template.render(stationId=stationId)
"""
# TODO: find parameter names in url.


def fetch_url_params(url):
    es1 = [s.split('}')[0] for s in url.split('{') if '}' in s]
    return {key: query_params[key] for key in es1}


def insert_url_params(url):
    if not '{' in url:
        return url
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(templatified(url))
    ps = fetch_url_params(url)
    return template.render(**ps)


def test_insertion():
    ep = '/products/types/{typeId}/{stationId}/{locationId}'
    ps = fetch_url_params(ep)
    u2 = insert_url_params(ep)
    print(ep)
    print(ps)
    print(u2)
    

# AHA!    brainwave!!!    Must take action to distinguish different error types
# in the test code.
# And distinguish validation error from endpoint error.

def nws_validate_and_call():
  try:
    rs = raw_swagger(local.swagger.nws)                              # global
    with httpx.Client(base_url=local.api_base.nws) as client:
        for ep in endpoint_names(rs):
            is_valid = nws_validator(ep)
            print(ep)
            print(is_valid.endpoint)
            ep0 = ep
            if ep in test_parameters:
                things = test_parameters[ep]
                ep = insert_url_params(ep)
                if ep0 != ep:
                    print('   calling .............', ep)
                for params in things['good']:
                    assert is_valid(params)
                    print('   ok good', params)
                    r = client.get(ep, params=params)
                    assert r.status_code == 200
                for params in things['bad']:
                    assert not is_valid(params)
                    print('   ok bad', params)
                    r = client.get(ep, params=params)
                    assert r.status_code != 404    # Bad endpoint
                    assert r.status_code in [400, 500]    # Bad Parameter
                    # or Server Error
                    # 500 from /zones/forecast/{zoneId}/stations
                    # with {'limit': '100'}

  finally:
    globals().update(locals())


def nws_call(endpoint, params=None):
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(endpoint, params=params)
        assert r.status_code == 200
    return r.json()


active_alerts = {
    'good': [
        { 'area': ['WY'], 'limit':   50, },
        { 'area': ['CO', 'KS', 'PK', 'PH'] },

        #        { 'xxxx':   'yyyyyyy', },    # additionalProperties permitted
        # but rejected by endpoint    400 Bad Request

        #        { 'zoneId':   'xxxxxx', },    # additionalProperties permitted
        # but rejected by endpoint    400 Bad Request

        { 'status':   ['actual', 'test'], }, 
        { 'message_type':   ['alert', 'cancel'], }, 
        { 'event':   ['Hard Freeze Warning', 'Dense Fog Advisory'], }, 
    ],
    'bad': [ 
            #        { 'limit':   '100', },
        # but accepted by endpoint
        { 'status':   ['xxxxxx'], }, 
    ],
}

# AHA!    brainwave!!!    Must take action to distinguish different error types
# in the test code.
# And distinguish validation error from endpoint error.
# /zones/forecast/{zoneId}/stations
zones_and_limits = {
    'good': [
        #        {  },   # valid but 500 Internal Server Error
        #        {
            #            'zoneId': 'WYZ433', 
            #    'limit':   50,
            #        },
            #        { 'zoneId': 'WYZ433', },   # valid but 400 Bad Request

            #            { 'limit':   5, },    # 500 error
        # TODO: investigate
        # 500 errors from /zones/forecast/{zoneId}/stations
        #        { 'xxxx':   'yyyyyyy', },    # additionalProperties permitted
    ],
    'bad': [ 
        { 'limit':   '100', },
        { 'zoneId':   'xxxxxx', },
    ],
}

zones = {
    'good': [
        #        { 'zone': 'WYZ433', },
        #{ 'zoneId': 'WYZ433', },
        #{ 'xxxx':   'yyyyyyy', },    # additionalProperties permitted
    ],
    'bad': [ 
        { 'zoneId':   'xxxxxx', },
    ],
}

start_end_limit = {
    'good': [
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   50,
        },
        { 'start': '2024-09-17T18:39:00+00:00', },
        { 'end': '2024-09-17T18:39:00+00:00', },
        { 'limit':   50, },
        {  },
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   '100', 
        },

        #        { 'start': '20240000-09-17T18:39:00+00:00', },
        # but rejected by endpoint    400 Bad Request

        #        { 'start': 'xxxxxxxx', },
        # but rejected by endpoint    400 Bad Request

        #        { 'x': 'yyyyyyy', },
        # but rejected by endpoint    400 Bad Request

    ],
    'bad': [ 
    ],
}

type_ids = {
    'good': [
        #        { 'typeId': 'ZFP', },
        #{ 'typeId': 'yyyyyyy', },
        #'ZFP', 'x', 1, {}, []      # anything goes!!!!!!!!!!!
        # but rejected by endpoint    400 Bad Request
    ],
    'bad': [ 
    ],
}

product_ids = {
    'good': [

        #        { 'productId': 'ZFP', },
        # but rejected by endpoint    400 Bad Request

        #        { 'productId': 'xxxxxx', },
        # but rejected by endpoint    400 Bad Request

        #        'ZFP', 'x', 1, {}, []      # anything goes!!!!!!!!!!!

    ],
    'bad': [ 
    ],
}



test_parameters = {
    '/alerts/active': active_alerts ,
    '/products/{productId}': product_ids ,
    '/products/types/{typeId}': type_ids ,
    '/stations/{stationId}/observations': start_end_limit ,
    '/zones/forecast/{zoneId}/observations' : zones,
    '/zones/forecast/{zoneId}/stations' : zones_and_limits,
} 



def alert_types():
    return nws_call('/alerts/types')['eventTypes']


def stations():
    js = nws_call('/stations')
    counties = set()                           # thing of interest
    for feat in js['features']:
        if 'county' in feat['properties']:
            counties.add(feat['properties']['county'])
    typ = [d['properties']['@type'] for d in js['features']]
    typ = sorted(list(set(t)))
    assert typ == ['wx:ObservationStation']             # thing of interest

    ids = [d['properties']['stationIdentifier'] for d in js['features']]
    oz = js['observationStations']
    assert type(oz) is list
    assert oz[-1].endswith(ids[-1])
    globals().update(locals())
    return ids             # thing of interest


def radar_stations():
    js = nws_call('/radar/stations')
    for feat in js['features']: pass

    typ = [d['properties']['@type'] for d in js['features']]
    typ = sorted(list(set(typ)))
    globals().update(locals())
    assert typ == ['wx:RadarStation']  # thing of interest

    station_types = [d['properties']['stationType'] for d in js['features']]
    station_types = sorted(list(set(styp)))
    globals().update(locals())
    assert station_types == ['Profiler', 'TDWR', 'WSR-88D']

    ids = [d['properties']['id'] for d in js['features']]
    return ids


def zone_ids():
    js = nws_call('/zones')
    for feat in js['features']: pass
    globals().update(locals())

    atypes = [d['properties']['@type'] for d in js['features']]
    atypes = sorted(list(set(atypes)))
    ttypes = [d['properties']['type'] for d in js['features']]
    ttypes = sorted(list(set(ttypes)))
    assert atypes == ['wx:Zone']
    assert ttypes == ['coastal', 'county', 'fire', 'offshore', 'public']
    globals().update(locals())
    ids = [d['properties']['id'] for d in js['features']]
    return sorted(list(set(ids)))


def product_codes():
    js = nws_call('/products/types')
    context = js['@context']
    things = js['@graph']
    for thing in things:
        pass
    globals().update(locals())
    return [d['productCode'] for d in things]


def nws_series():
  try:
    """ Get a series of observations suitable for putting in a pandas DF,
    and then a jupyter notebook.
    """
    # Data
    ep1 = '/stations/{stationId}/observations'
    # TODO: validate stationId ??????
    stationId = 'KRCM'    # OK
    stationId = 'CO100'   # OK
#'089SE', '0900W'
    params = {
        'start': '2024-09-17T18:39:00+00:00', 
        'end':   '2024-09-18T18:39:00+00:00',
        'limit':   50,
    }

    # Validate params
    rs = raw_swagger(local.swagger.nws)                              # global
    with_refs = jsonref.loads(json.dumps(rs))
    vinfo = with_refs['paths'][ep1]['get']['parameters']             # per API
    schema = schema_trans(vinfo)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    assert validator.is_valid(params)

    # Insert stationId into endpoint path
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(templatified(ep1))
    ep = template.render(stationId=stationId)

    # Call the endpoint and verify status_code.
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(ep, params=params)
        assert r.status_code == 200

    # Extract desired data from response.
    final = []
    feats = r.json()['features']
    for ft in feats: 
        pt = ft['properties']
        for key in [ '@id', '@type', 'elevation', 'station', 'rawMessage', 'icon', 'presentWeather', 'cloudLayers', 'textDescription', ]:
            pt.pop(key)
        for key in pt:
            if type(pt[key]) is dict:
                pt[key] = pt[key]['value']
        final.append(pt)

    # Convert to dataframe.
    df = pandas.DataFrame(final)
    assert df.shape == (50, 15)
#    return df
  finally:
    globals().update(locals())


def templatified(s):
    return s.replace('{', '{{').replace('}', '}}')


def schema_trans(schema_list):
    return {'properties': {thing['name']: thing['schema'] for thing in schema_list} }


# out
# out
# #######
# out
# out


def more_validation():
    good_ones = [
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   50,
        }
    ]
    bad_ones = [ 
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   '100',     # works OK at the endpoint but fails validation
        },
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   501,    # fails validation as it should
        }
    ]
    for params in bad_ones:
        assert not validator.is_valid(params)
    for params in good_ones:
        assert validator.is_valid(params)


def demo_jinja():
    s = '/stations/{stationId}/{observations}'
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(templatified(s))
    tr = template.render(stationId='xxxxxxx')
    assert tr == '/stations/xxxxxxx/'


# TODO: a schema would make a good template.
"""
{ 
  'properties': {{properties}} 
  {{other_attributes}} 
  {{etc}} 
} 
"""


# TODO: 
# Fix data duplication in the form of
# ep1 = '/stations/{stationId}/observations'
# ep = f'/stations/{stationId}/observations'
# Both are required.
# ep1 for pulling validation info from swagger.
# ep for calling the endpoint.
# No hay manera a cambiar ep1 en ep.
# but, this reminds me of jinja.
# Maybe worth using to avoid that duplication.
# Definitely worth using to refresh myself on jinja.
# FIXED


# TODO: research questions
# for Theresa
# rt teaching middle-schoolers about CyberSecurity.
# 
#
# Meet Tue at 1:00 - 2:00


