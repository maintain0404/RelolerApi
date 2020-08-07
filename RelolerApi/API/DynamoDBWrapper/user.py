from .base import *
import jsonschema
import os

class User(BaseItemWrapper):
    def __init__(self, nickname):
        super().__init__("USER", nickname)

    def to_internal(self, new_data):
        try:
            pass
        except jsonschema.exceptions.ValidationError:
            return False
        else:
            pass
        