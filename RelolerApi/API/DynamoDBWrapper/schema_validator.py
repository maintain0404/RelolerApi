import jsonschema
import os
import functools
import json

schema_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schemas')

class InvalidSchemaException(Exception):
    def __init__(self):
        super().__init__("Invalid dictionary shema")

    post_input_schema_file = open(os.path.join(schema_directory, 'post_input.json'), encoding = 'UTF-8')
    post_input_schema = json.loads(post_input_schema_file.read())
    PostValidator = functools.partial(jsonschema.validate, 
    schema = post_input_schema
    )
def post_is_valid(data):
    try:
        PostValidator(instance = data)
    except jsonschema.exceptions.ValidationError:
        return False
    else:
        return True