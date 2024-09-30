from protein_test_data import test_parameters
import json

import httpx      # similar to R data frames
import pandas      # similar to R data frames
import jsonref     # cross platform
import jsonschema     # cross platform
from jsonschema import validate     # cross platform
from jsonschema import (     # cross platform
    Draft7Validator,
    FormatChecker,
)

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    namespacify,
    endpoint_names,
    insert_endpoint_params,
)
from some_code import schema_trans

from pprint import pprint

#https://www.ncbi.nlm.nih.gov/genbank/samplerecord/
#                    Examples: A2BC19, P12345, A0A023GPI8
sample_query_params = {
    'accession': test_parameters['/proteins']['good'][0]['accession'],
}


# https://www.ebi.ac.uk/proteins/api/doc/#!/taxonomy/getTaxonomyLineageById
# shows /taxonomy endpoints but these are not present in the OpenAPI file.


def get_component_schemas_protein():    # EBI
  try:
    rs = raw_swagger(local.swagger.protein)
    with_refs = jsonref.loads(json.dumps(rs))
    components = with_refs['components']
    return components['schemas']
  finally:
    globals().update(locals())


def protein_validator(endpoint):
  try:
    """Return a function to validata parameters for `endpoint`.
    >>> params = dict(x=1)
    >>> assert nws_validator('/foo/{bar}/bat')(params) is True
    >>> is_valid = nws_validator('/foo/{bar}/bat')
    >>> assert is_valid(params) is True
    # TODO: consider name change.
    """
    rs = raw_swagger(local.swagger.protein)     # protein vs nws
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    try:
        vinfo = thing['parameters'] if 'parameters' in thing else thing['get']['parameters']
    except KeyError:
        is_valid = lambda ob: 'unknown'
        schema = None
        return is_valid
    schema = schema_trans(vinfo)     # NWS-specific
    assert list(schema.keys()) == ['properties']
#    print(endpoint, list(schema['properties'].keys()))
    is_valid = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)
    return is_valid
  finally:
    is_valid.endpoint = endpoint
    is_valid.schema = schema
    globals().update(locals())


head = {'accept': 'application/json'}  # some endpoints default to XML.


def protein_validate_and_call():
  try:
    rs = raw_swagger(local.swagger.protein)       # protein
    with httpx.Client(base_url=local.api_base.protein) as client:   # protein
        for ep in endpoint_names(rs):
            is_valid = protein_validator(ep)
            print(ep)
            ep0 = ep
            if ep in test_parameters:
                things = test_parameters[ep]
                ep = insert_endpoint_params(ep, sample_query_params)
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


# NOT specific to NWS except for base_url
def nws_call(endpoint, params=None):
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(endpoint, params=params)
        assert r.status_code == 200
    return r.json()


# xxx data ##################################################################


def nws_series():
  try:
    """ Get a series of observations suitable for putting in a pandas DF,
    and then a jupyter notebook.
    """
    # Data
    ep1 = '/stations/{stationId}/observations'
    # TODO: validate stationId ??????
#'089SE', '0900W'
    stationId = 'KRCM'   # OK
    stationId = 'CO100'   # OK
    # NOTE  stationId cannot go in params.
    params = {                                # OK
        'start': '2024-09-22T23:59:59+00:00', 
        'end':   '2024-09-23T23:59:59+00:00', 
        'limit':   50,
    }

    # Validate params
    assert nws_validator(ep1)(params)

    # Insert stationId into endpoint path
    ep = insert_endpoint_params(ep1, locals())

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
#    assert df.shape == (50, 15)
    assert df.shape[1] == 15
    return df
  finally:
    globals().update(locals())



ps = get_component_schemas_protein()
assert len(ps.keys()) == 96
pt = ps['ProteinType']
st = ps['SequenceType']
s = ps['Sequence']
# Nice schemas.  Each entry in every schema has 'xml': {'attribute': True},
# which code be eliminated w/o effect.


