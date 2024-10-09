
# 

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

generic_bad = ['' , 0, 'foo', {}] 
generic_bad = ['' , 0, 'foo'] 

uploadImage_post = {
    'good': [
      {
       'petId': 1234,
       'additionalMetadata': 'aaaaaaa',
       'file': 'ffffff',
      }, 
      {
       'petId': 1234,
      }, 
    ],
    'bad': generic_bad,
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
    'bad': generic_bad
}
Pet_put = {
    'good': [
      {
       'photoUrls': [],
       'name': 'buff',
      }, 
      {
       'photoUrls': [],
       'name': 'buff',
       'status': 'pending',
      }, 

    ],
    'bad': generic_bad
}

Pet_findByStatus = {
    'good': [
      ['sold', ], 
      ['sold', 'pending'], 
    ],
    'bad': generic_bad
}
Pet_findByTags = {
    'good': [
      ['foo', ], 
      ['foo', 'bar'], 
    ],
    'bad': generic_bad
}


petId_get = {
    'good': [1234, 0, 58806647],
    'bad': ['', 'foo'],
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
    'bad': generic_bad,
}

store_inventory = {
    'good': [],
    'bad': [],
}

store_order_post = {
    'good': [ {
         'id': 4321,
         'petId': 1234,
        }, 
        {
         'petId': 1234,
        }, 
        {},
    ],
    'bad': generic_bad,
}
store_order_get = {
    'good': [ 1, 9, ],
    'bad': [0, 99, 'x']
}
store_order_delete = {
    'good': [ 1, 9],
    'bad': [0, 'x']
}

user_delete = {
    'good': [ {
         'username': 'Auser',
        }, 
    ],
    'bad': [{}],
}

user_login_get = {
    'good': [ {
         'password': 'xxxx',
         'username': 'Auser',
        }, 
    ],
    'bad': [{}],
}

user_logout_get = {
    'good': [], 
    'bad': [],
}

user_with_array_post = {
    'good': [ [{
         'id': 1234,
         'username': 'Auser',
        }], 
        [{}],
    ],
    'bad': generic_bad,
}

user_get = {
    'good': [ 'user1', 'bar' ],
    'bad': [0],
}
user_put = {
    'good': [ {
         'username': 'user1',
         'body': {},
        }, 
    ],
    'bad': generic_bad,
}

user_post = {
    'good': [ {
         'id': 1234,
         'username': 'Auser',
        }, 
        {},
    ],
    'bad': generic_bad,
}


# TODO: data sources...
# TODO: postman petstore
# TODO: postman nws
# etc


test_parameters = {
    '/pet/{petId}/uploadImage': {
        'post': uploadImage_post ,
    },
    '/pet': {
        'post': Pet_post ,
        'put': Pet_put,
    },
    '/pet/findByStatus': {
        'get': Pet_findByStatus,
    },
    '/pet/findByTags': {
        'get': Pet_findByTags,
    },

    '/pet/{petId}': {
        'get': petId_get,
        'post': petId_post,
        'delete': petId_delete,
    },

    '/store/inventory': {
        'get': store_inventory,
    },
    '/store/order': {
        'post': store_order_post,
    },
    '/store/order/{orderId}': {
        'get': store_order_get,
        'delete': store_order_delete,
    },

    '/user/login': {
        'get': user_login_get 
    },
    '/user/logout': {
        'get': user_logout_get 
    },
    '/user/createWithArray': {
        'post': user_with_array_post,
    },
    '/user/createWithList': {
        'post': user_with_array_post,
    },
    '/user/{username}': {
        'get': user_get ,
        'put': user_put ,
        'delete': user_get ,
    },

    '/user': {
        'post': user_post ,
    },
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
