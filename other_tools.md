
### other language

- https://github.com/APIDevTools/swagger-parser    javascript
- https://github.com/swagger-api/swagger-parser    java pojo


### defunct

    - https://pypi.org/project/swagger-parser/    no release since 2017

### current

    - https://pypi.org/project/openapi-python-client/
    - https://openapi-core.readthedocs.io/en/latest/
    - https://libraries.io/pypi/prance

    - https://github.com/manchenkoff/openapi3-parser
    - https://github.com/manchenkoff/openapi3-parser/blob/master/src/openapi_parser/builders/common.py

see `merge_schema` function.  See if it duplicates `dict.update`.
It does not.  But the code is rigid.  Shows signs of inattention to detail.


ugh.
Turns out extracting the validators is irritating.
There are several existing libs for parsing OpenAPI.
Try them out.

```
import json.tool   # cli
from openapi_core import OpenAPI
openapi = OpenAPI.from_file_path(pet_swagger_full)
```

has format validators
such as: date, date-time, binary, uuid or byte.
raises error if request is invalid

    openapi.validate_request(request)

but apparently can only validate a request, no validating data independent of
request.
otoh, if it truly validates then apparently it has a way of reliably
extracting the schema.

And it has `unmarshalling`
https://openapi-core.readthedocs.io/en/latest/unmarshalling.html
which means converting strings to python types; datetime, uuid, etc.
^ Handy stuff ^


```
from prance import ResolvingParser
parser = ResolvingParser(pet_swagger_full)
parser.specification # contains fully resolved specs as a dict
```


    prance.util.path is interesting.
    Similar to my deep_fetch stuff.
    btw, could do deep_set.
    https://github.com/RonnyPfannschmidt/prance/blob/main/prance/util/path.py
    Written by one guy.


These three are the competion I've located so far.  All three have good
qualities but also drawbacks.  tldr; None can reliably parse out the schema
definitions the way I want.
I suspect.
Keep researching a bit more.
While continuing with my own.


- https://github.com/wy-z/requests-openapi
- https://tools.openapis.org
- https://github.com/commonism/aiopenapi3   pydantic-centric
- https://github.com/schemathesis/schemathesis  automated api testing
- https://github.com/playpauseandstop/rororo   schema-first approach
- https://github.com/namuan/http-rider  interesting but GUI
- https://github.com/commonism/aiopenapi3 tbi

tbi == to be investigated



