from .base import *

class Post(BaseItemWrapper):
    def __init__(self, pk = None, sk = None):
        if not ((pk and sk) or (not pk and not sk)):
            raise InvalidPrimaryKeyError
        if not pk:
            pk = 'testpk0'
        if not sk:
            sk = SK.make_new('post')
        super().__init__(pk, sk)

class Posts(BaseQueryWrapper):
    def __init__(self, pk):
        super().__init__(pk)