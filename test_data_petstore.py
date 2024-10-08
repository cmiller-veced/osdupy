

# valid UniProtKB accession

petIds = {
    'good': [1234, '1234', ],
    'bad': ['x', '', '0', 0, ],
}
file = {
    'good': ['1234', 'foo'],
    'bad': ['' , 0, ],
}
status = {
    'good': ['', ''],         # fill in with real data.
    'bad': ['' , 0, 'foo'],
}
petName = {
    'good': ['fluff', 'x'],
    'bad': ['' , 0, []],
}
api_key = {
    'good': ['a?', 'string?'],
    'bad': ['' , 0, 'foo'],
}


orderId = {
    'good': ['', ''],
    'bad': ['' , 0, 'foo'],
}

username = {
    'good': ['', ''],
    'bad': ['' , 0, 'foo'],
}

x = {
    'good': ['', ''],
    'bad': ['' , 0, 'foo'],
}
photoUrls = {
    'good': [[''], []],
    'bad': ['' , 0, 'foo'],
}
category = {
    'good': [{}, {'foo': 'bar'}],
    'bad': ['' , 0, 'foo'],
}
# TODO: put together atomic parameters.    Maybe.

api_key = 'special-key'   # which actually works.

# endpoint: /pet  verb: POST
from_postman_online = {
  "name": "doggie",
  "photoUrls": [
    "adipisicing",
    "non et"
  ],
  "id": 73291872,
  "category": {
    "id": -97087948,
    "name": "incididunt cupidatat nostrud"
  },
  "tags": [
    {
      "id": -41459971,
      "name": ""
    },
    {
      "id": -75303293,
      "name": "mollit"
    }
  ],
  "status": "sold"
}


Pet_post = {
    'good': [
      {
       'id': 1234,
       'category': {},
       'name': 'fluff',
       'photoUrls': [],
       'status': 'available',
       'tags': [],
      }, 
      from_postman_online,
    ],
    'bad': ['' , 0, 'foo', {}],
}
Pet_put = {
    'good': [
      {
       'id': 1234,
       'name': 'buff',
      }, 
    ],
    'bad': ['' , 0, 'foo', {}],
}


petId_get = {
    'good': [1234, '1234', 58806647],
    'bad': ['' , 0, 'foo'],
}

petId_post = {
    # TODO: start here
    'good': [ {
         'petId': 1234,
         'name': 'fluff',
         'status': 'available',
        }, 
    ],
    'bad': ['' , 0, 'foo', {}],
}

petId_delete = {
    'good': [ {
         'petId': 1234,
         'api_key': api_key,
        }, 
    ],
    'bad': ['' , 0, 'foo', {}],
}


# TODO: data sources...
# TODO: postman petstore
# TODO: postman nws
# etc
# etc


test_parameters = {
    #    '/pet/{petId}/uploadImage': proteins_accession ,
    '/pet': {
        'post': Pet_post ,
        'put': Pet_put,
    },
    '/pet/{petId}': {
        'get': petId_get,
        'post': petId_post,
        'delete': petId_delete,
    },

    #    '/pet/findByStatus': proteome ,
    #    '/pet/findByTags': proteome ,
} 



'''
class CallSpecificEndpoint(PydanticModel):
    """
    The information content of this class is exactly equivalent to saying,
    'It's a POST call.'
    """
    parameters: dict

and then there was the Neptune database.
Gremlin queries translated to the above, one-trick.

'''

# good_ones = [
#     {"name": 'kittyX', 'photoUrls': []},
#     {"name": 'kittyX', 'photoUrls': [], 'category': {}},
#     {"name": 'kittyX', 'photoUrls': [], 'status': 'sold'},
#     {"name": 'kittyX', 'photoUrls': [], 'category': {}, 'status': 'sold'},
# ]
# bad_ones = [
#     {},
#     {"name": 'kittyX'},
#     {"name": 'kittyX', 'photoUrls': [], 'category': ''}, 
#     {"name": 'kittyX', 'photoUrls': [], 'status': ''},
# ]


