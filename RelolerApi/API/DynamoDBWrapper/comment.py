from .base import *

class CommentList(BaseQueryWrapper):
    def __init__(self, pk, sk):
        super().__init__(pk = pk, sk = sk)
