from nws_test_data import test_parameters
import json
from collections import defaultdict
from pprint import pprint

import jmespath
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
    local,        # not a tool.  It is data.
    namespacify,
    endpoint_names,
)


def get_component_schemas_nws():    # NWS
    rs = raw_swagger(local.swagger.nws)
    with_refs = jsonref.loads(json.dumps(rs))
    components = with_refs['components']
    for key in ['responses', 'headers', 'securitySchemes']:
        components.pop(key)
    parameters = components['parameters']
    components['parameters'] = {key: parameters[key]['schema'] for key in parameters}
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


# TODO: spiff up
####################### Insert query params ########################

query_params = {
    'productId': 'ZFP',
    'typeId': 'tttttt',
    'zoneId': 'WYZ432',
    'stationId': 'CO100',
    'locationId': 'llllll',
}


# temporary hard-coded solution
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
 

####################### ^ Insert query params ^ ########################


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


# general
def templatified(s):
    return s.replace('{', '{{').replace('}', '}}')


# NWS-specific (but who knows who else might do the same).
def schema_trans(schema_list):
    return {'properties': {thing['name']: thing['schema'] for thing in schema_list} }


# NWS data ##################################################################

def alert_types():
    return nws_call('/alerts/types')['eventTypes']


def stations():
    js = nws_call('/stations')
    counties = set()                           # thing of interest
    for feat in js['features']:
        if 'county' in feat['properties']:
            counties.add(feat['properties']['county'])
    typ = [d['properties']['@type'] for d in js['features']]
    typ = sorted(list(set(typ)))
    assert typ == ['wx:ObservationStation']             # thing of interest
    ids = [d['properties']['stationIdentifier'] for d in js['features']]
    oz = js['observationStations']
    assert type(oz) is list
    assert oz[-1].endswith(ids[-1])   # duplicated info
    globals().update(locals())
    return ids


def radar_stations():
    js = nws_call('/radar/stations')
    typ = [d['properties']['@type'] for d in js['features']]
    typ = sorted(list(set(typ)))
    assert typ == ['wx:RadarStation']  # thing of interest
    station_types = [d['properties']['stationType'] for d in js['features']]
    station_types = sorted(list(set(station_types)))
    assert station_types == ['Profiler', 'TDWR', 'WSR-88D']  # thing of interest
    return [d['properties']['id'] for d in js['features']]


def zone_ids():
    js = nws_call('/zones')
    atypes = [d['properties']['@type'] for d in js['features']]
    atypes = sorted(list(set(atypes)))
    ttypes = [d['properties']['type'] for d in js['features']]
    ttypes = sorted(list(set(ttypes)))
    assert atypes == ['wx:Zone']
    assert ttypes == ['coastal', 'county', 'fire', 'offshore', 'public']
    ids = [d['properties']['id'] for d in js['features']]
    return sorted(list(set(ids)))


def product_codes():
    js = nws_call('/products/types')
    context = js['@context']
    things = js['@graph']
    return [d['productCode'] for d in things]

# ^ NWS data ^ ###############################################################


# Fetch a data set suitable for a pandas dataframe.
# ############################################################################


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
    return df
  finally:
    globals().update(locals())


