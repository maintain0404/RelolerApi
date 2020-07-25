class InvalidSchemaException(Exception):
    def __init__(self):
        super().__init__("Invalid dictionary shema")

class SchemaValidator:
    def __init__(self, valid_schema):
        self.schema = valid_schema

    def 