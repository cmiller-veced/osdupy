import json
import os
from functools import singledispatch  # for heterogeneous recursive data structure


pet_swagger = 'https://petstore.swagger.io/v2/swagger.json'
pet_swagger_local = '~/local/petstore/swagger.json'


def raw_swagger(at_path):
    with open(os.path.expanduser(at_path)) as fh:
        return json.load(fh)


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

