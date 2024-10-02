import json
from collections import defaultdict
from pprint import pprint

import jmespath     # cross platform
import httpx        # 
import pytest
import pandas      # similar to R data frames
import jsonref     # cross platform
import jsonschema     # cross platform
from jsonschema import validate     # cross platform
from jsonschema import (     # cross platform
    Draft7Validator,
    FormatChecker,
)
from jinja2 import Environment, PackageLoader, select_autoescape     # cross platform

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    namespacify,
    endpoint_names,
)


def schema_trans(schema_list):
    return {'properties': {thing['name']: thing['schema'] for thing in schema_list} }


