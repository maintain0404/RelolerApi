import json

class SchemaValidator:
    def __init__(self, json, dict_to_check):
        assert isinstance(json, dict)(
            'Must use json(dict) object'
        )
        self.valid_schema = json

    def 