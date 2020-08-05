from .base import *
import jsonschema
import os

class User(BaseItemWrapper):
    def __init__(self, nickname):
        super().__init__("USER", nickname)

        