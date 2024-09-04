import json
import os


pet_swagger = 'https://petstore.swagger.io/v2/swagger.json'
pet_swagger_local = '~/local/petstore/swagger.json'


def raw_swagger(at_path):
    with open(os.path.expanduser(at_path)) as fh:
        return json.load(fh)


def go():
    rs = raw_swagger(pet_swagger_local)
    print(len(str(rs)))
    print(len(rs))


go()

