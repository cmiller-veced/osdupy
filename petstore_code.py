

def get_endpoint_schemas_pets():   # petstore
  try:
    schemas = {}
    rs = raw_swagger(local.swagger.pet)
    with_refs = jsonref.loads(json.dumps(rs))
    paths = list(with_refs['paths'].keys())
    for path in paths:
        print(path)
        path_info = with_refs['paths'][path]
        schemas[path] = {}
        for verb in list(path_info.keys()):
            print(f'  {verb}')
            verb_info = path_info[verb]
            params = verb_info['parameters']
            for param_info in params:
                schema = param_info['schema'] if 'schema' in param_info else param_info
                schemas[path][verb] = dict(schema)
    return schemas
  finally:
    globals().update(locals())



def petstore_calls():
  try:
    with httpx.Client(base_url=local.api_base.pet) as client:
        ep = '/pet/findByStatus'

        vd = validator_for(ep, 'get')
        params = ['available', 'sold']  # passes validation but returns []
        vd(params)
#        a job for preprocessing ?

        r = client.get(ep, params=params)
        assert r.status_code == 200
        foo = r.json()
        assert foo == []
        # OK.  There is a successful GET request.

        params = {'status': 'available'}  # good result but fails validation
        r = client.get(ep, params=params)
        foo = r.json()
        assert len(foo) > 11
        with pytest.raises(jsonschema.exceptions.ValidationError):
            vd(params)

        ep = '/pet'
        params = {"name": 'kittyX', 'photoUrls': [], 'category': {}, 'status': 'sold'}
        header = {'Content-Type': 'application/json'}
        vd2 = validator_for(ep, 'post')
        vd2(params)
        r2 = client.post(ep, data=json.dumps(params), headers=header)
        assert r2.status_code == 200
        assert r2.reason_phrase == 'OK'
        # OK.  There is a successful POST request.

        ep = '/user'
        user_data = {
          "id": 0,
          "username": "string",
          "firstName": "string",
          "lastName": "string",
          "email": "string",
          "password": "string",
          "phone": "string",
          "userStatus": 0
        }
        vd3 = validator_for(ep, 'post')
        vd3(user_data)
        headers = {'Content-Type': 'application/json'}
        r3 = client.post(ep, data=json.dumps(user_data), headers=headers)
        assert r3.status_code == 200
        assert r3.reason_phrase == 'OK'
        # OK.  Another successful POST request.
 
  finally:
    globals().update(locals())







def validator_for(endpoint, verb):     # petstore
    schema = get_endpoint_schemas_pets()[endpoint][verb]
    if 'required' in schema and schema['required'] is True:  # preprocessing
        del schema['required'] 
    fun = lambda ob: validate(ob, schema=schema)
    fun.endpoint = endpoint
    fun.verb = verb
    fun.schema = schema
    return fun


