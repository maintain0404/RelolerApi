from .table_base import TableBaseList, SK

class CommentList(TableBaseList):
    def __init__(self):
        super().__init__()

    def create(self, pk, comment_meta):
        item = dict()
        item['pk'] = pk
        item['sk'] = SK.make('comment')
        item['comment_meta'] = comment_meta

        self._create_item(item)

    def delete(self, pk, sk):
        return self._delete_item(pk, sk)

    def read(self, pk):
        return self._query(pk)['Items']

    def update(self, pk, sk, comment_meta):
        pass