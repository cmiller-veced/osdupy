import json
import os
from functools import singledispatch  # for heterogeneous recursive data structure

import jsonref
import jsonschema
from jsonschema import validate


pet_swagger = 'https://petstore.swagger.io/v2/swagger.json'
pet_swagger_local = '~/local/petstore/swagger.json'


def raw_swagger(at_path):
    with open(os.path.expanduser(at_path)) as fh:
        return json.load(fh)


# Validation using jsonschema #
# ######################################################################## #

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


validate_jsonschema_with_refs()


# Working with json data #
# ######################################################################## #

# Right away after parsing we face the problem of making sense of a big, gnarly
# json doc.  Rather than give up and revert to imitating java in python we deal
# with it.  Using the standard library.

# aside
# Recursion over a heterogeneous data structure.
@singledispatch
def recur(arg, indent=0):
    print(f'{" "*indent}{arg}')

@recur.register
def _(arg: list, indent=0):
    for thing in arg:
        recur(thing, indent=indent+1)

@recur.register
def _(arg: dict, indent=0):
    for key in arg:
        recur(key, indent=indent+1)
        recur(arg[key], indent=indent+1)
        print()

# This is another side of the functional/OO thingy.  A generic function, in
# other words a function that operates differently on differing types.

# It turns out the  Python language has this amazing thing that makes it easy to
# work with json data.  It's called the Python language.  Not some third party
# library.  "batteries included" means it has a lot of amazing features out of
# the box.  So we can do amazing things in a few lines.  Why use a third party
# library when you can do that?
#
# btw, each 3rd party library adds complexity.  We should account for that in
# meeasurements of complexity.
# and cognitive load.
# 
# In addition to adding overhead at deployment time, each 3rd party lib tends to
# have its own way of looking at the world.  When we adopt the lib we have to
# think in that way.  There's nothing wrong with that.  But if it distracts from
# the problem at hand then we have to devote some of our limited mental capacity
# to that.  Each such context switch adds up.


def go():
  try:
    rs = raw_swagger(pet_swagger_local)
    print(len(str(rs)))
    print(len(rs))
    rs_keys = ['swagger', 'info', 'host', 'basePath', 'tags', 'schemes', 'paths', 'securityDefinitions', 'definitions', 'externalDocs']
    assert sorted(list(rs.keys())) == sorted(rs_keys)
    for key in rs_keys:
        print(key, type(rs[key]))
        print(rs[key])
        print()
    recur(rs)

  finally:
    globals().update(locals())


go()

