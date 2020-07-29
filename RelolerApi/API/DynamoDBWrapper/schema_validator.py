from jsonschema import validate
import os

schema_directory = os.path.join(os.getcwd(), 'schemas')

class InvalidSchemaException(Exception):
    def __init__(self):
        super().__init__("Invalid dictionary shema")

class SchemaValidator:
    def __init__(self, schema):
        self.schema = valid_schema

    def validate(self, data):
        validate(instance = data, schema = self.schema)

    def datas_to_be_inputed(self):
        for x in self.schema:
            if x.has('description')

PostValidator = jsonschema(schema = os.path.join(schema_directory, 'post_schema.json'))