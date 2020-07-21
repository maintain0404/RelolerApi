import json

class SchemaValidator:
    def __init__(self, schema_json):
        assert isinstance(schema_json, dict)(
            'Must use json(dict) object'
        )
        self.valid_schema = json