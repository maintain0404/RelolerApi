from .base import BaseItemWrapper, TableBaseList, SK, InvalidPrimaryKeyError, BaseQueryWrapper

class Post(BaseItemWrapper):
    def __init__(self, pk = None, sk = None):
        if (pk and sk) or (not pk and not sk):
            raise InvalidPrimaryKeyError
        if not pk:
            pk = 
        if not sk:
            sk = SK.make_new('post')
        super().__init__(pk, sk)

class Posts(BaseQueryWrapper):
    def __init__(self, pk):
        super().__init__(pk)