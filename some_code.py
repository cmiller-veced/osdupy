import json
import os
from functools import singledispatch  # for heterogeneous recursive data structure


pet_swagger = 'https://petstore.swagger.io/v2/swagger.json'
pet_swagger_local = '~/local/petstore/swagger.json'


def raw_swagger(at_path):
    with open(os.path.expanduser(at_path)) as fh:
        return json.load(fh)


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

