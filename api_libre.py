# TODO: fooooeeeeeeey!
# TODO: fooooeeeeeeey!
# TODO: fooooeeeeeeey!
# TODO: fooooeeeeeeey!
# TODO: fooooeeeeeeey!
# TODO: fooooeeeeeeey!
# TODO: fooooeeeeeeey!
# Requires APIkey and $
# Requires APIkey and $
# Requires APIkey and $
# Requires APIkey and $
# Requires APIkey and $
# Requires APIkey and $
# Requires APIkey and $
# or run locally.
# python -m pip install libretranslate => downgrades of multiple packages eg
# numpy

# TODO: try cmd2 in place of cmd.
import cmd2
import cmd2
import cmd2
import cmd2
import cmd2
import cmd2
import gnureadline



from libre_test_data import test_parameters
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

head = {'accept': 'application/json'}  # 
#sample_query_params = { 'accession': test_parameters['/proteins']['good'][0]['accession'], }


def get_component_schemas_libre():    #  # TODO: rename func
  try:

    rs = raw_swagger(local.swagger.libre)
    with_refs = jsonref.loads(json.dumps(rs))
    defs = with_refs['definitions']
    return defs
  finally:
    globals().update(locals())


def schema_trans(schema_list):
    d = {}
    for thing in schema_list:
        d['name'] = thing['schema'] if 'schema' in thing else {}
    return {'properties': d}
#    return {'properties': {thing['name']: thing['schema'] for thing in schema_list} }


def validator_func(openapi_file, endpoint):
  try:
    """Return a function to validata parameters for `endpoint`.
    """
    rs = raw_swagger(openapi_file)     # protein vs nws vs libre
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    assert len(thing.keys()) == 1
    verb = list(thing.keys())[0]
    tv = thing[verb]
    if 'parameters' in tv:
        vinfo = tv['parameters']
    else:
        vinfo = {}

#    for sting in vinfo: sting['schema']

#    try: vinfo = thing['parameters'] if 'parameters' in thing else thing['get']['parameters']
#    except KeyError:
#        is_valid = lambda ob: 'unknown'
#        schema = None
#        return is_valid
    schema = schema_trans(vinfo)     # 
    assert list(schema.keys()) == ['properties']
#    print(endpoint, list(schema['properties'].keys()))
    is_valid = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)
    return is_valid
  finally:
    globals().update(locals())
    is_valid.endpoint = endpoint
    is_valid.schema = schema


api_file_path = local.swagger.libre
api_base = local.api_base.libre

# ['/detect', '/frontend/settings', '/languages', '/suggest', '/translate', '/translate_file'])
flip = True
if not flip:
    endpoint = '/languages'
    endpoint = '/detect'
    is_valid = validator_func(local.swagger.libre, endpoint)
    data = {'q': 'Que idioma es?'}
    assert is_valid(data)
    data = {'x': 'Que idioma es?'}
    assert is_valid(data)
    data = {'q': 55}
    assert not is_valid(data)

if flip:
    endpoint = '/frontend/settings'
    endpoint = '/translate_file'
    openapi_file = api_file_path
    rs = raw_swagger(openapi_file)     # protein vs nws vs libre
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    verb = list(thing.keys())[0]
    tv = thing[verb]
#    vinfo = tv['parameters']
    is_valid = validator_func(local.swagger.libre, endpoint)


def validate_and_call():
  try:
    rs = raw_swagger(api_file_path)       # 
    with httpx.Client(base_url=api_base) as client:   # 
        verb_map = dict(get=client.get, post=client.post)
        for ep in endpoint_names(rs):
#            print(ep)
            ep_info = rs['paths'][ep]
            print(ep, list(ep_info.keys()))
            ep0 = ep
            is_valid = validator_func(api_file_path, ep)
#            print('     ', is_valid.schema)
            if ep in test_parameters:
                things = test_parameters[ep]
#                ep = insert_endpoint_params(ep, sample_query_params)
                if ep0 != ep:
                    print('   calling .............', ep)
                for params in things['good']:
                    assert is_valid(params)
                    print('   ok good valid', params)
                    fetch = verb_map[list(ep_info.keys())[0]]
                    r = fetch(ep, params=params, headers=head)
                    assert r.status_code == 200
                    # running locally

                    rj = r.json()
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


def translate(params):
    endpoint = '/translate'
    api_base = local.api_base.libre
    with httpx.Client(base_url=api_base) as client:
        r = client.post(endpoint, params=params)
        globals().update(locals())
        assert r.status_code == 200
    return r.json()


params = {}
params = {'q': 'What language is this?', 'source': 'en', 'target': 'es'}
tp = translate(params)


def es2ingles(phrase):
    params = {'q': phrase, 'source': 'es', 'target': 'en'}
    endpoint = '/translate'
    api_base = local.api_base.libre
    with httpx.Client(base_url=api_base) as client:
        r = client.post(endpoint, params=params)
    return r.json()['translatedText']

def en2spanish(phrase):
    params = {'q': phrase, 'source': 'en', 'target': 'es'}
    endpoint = '/translate'
    api_base = local.api_base.libre
    with httpx.Client(base_url=api_base) as client:
        r = client.post(endpoint, params=params)
    return r.json()['translatedText']


import cmd, sys
from turtle import *
import readline
import os

histfile = os.path.expanduser('~/.trans_history')
histfile_size = 1000000

class TurtleShell(cmd.Cmd):
    intro = 'Welcome to the trans shell.   Type help or ? to list commands.\n'
    prompt = '(trans) '
    file = None
    mode = 'es'
    mode_map = dict(es=es2ingles, en=en2spanish)

    
# TODO: how to save cmd.Cmd history separate from ordinary python history.
#     # Saves regular python in addition to the cmd loop.
#     def preloop(self):
#         if readline and os.path.exists(histfile):
#             readline.read_history_file(histfile)
#  
#     def postloop(self):
#         if readline:
#             readline.set_history_length(histfile_size)
#             readline.write_history_file(histfile)


    # ----- commands -----
    def do_mode(self, arg):
        if arg:
            self.mode = arg
        msg = f'the current mode is : {self.mode}'
        print(msg)

    def default(self, arg):
        func = self.mode_map[self.mode]
        print(func(arg))

    def do_exit(self,*args):
        return True


def go():
    TurtleShell().cmdloop()




def languages():
    endpoint = '/languages'
    api_base = local.api_base.libre
    with httpx.Client(base_url=api_base) as client:
        r = client.get(endpoint, params=params)
        globals().update(locals())
        assert r.status_code == 200
    return r.json()

if 0:
    lan = languages()
    for sub in lan:
        print(sub['code'], sub['name'],) 


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


