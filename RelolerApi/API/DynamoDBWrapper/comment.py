from .base import BaseQueryWrapper, SK

class CommentList(BaseQueryWrapper):
    def __init__(self, pk):
        super().__init__(pk)
