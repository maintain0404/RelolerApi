from .table_base import TableBase, current_time

class Comment(TableBase):
    def __init__(selfr):
        super().__init__()

     def create(self, pk, comment_meta):
        item = dict()
        item['id'] = pk
        item['sk'] = self.SK_POST + current_time()
        item['comment_meta'] = comment_meta

        self._create_item(item)

    def delete(self, pk, sk):
        return self._delete_item(pk, sk)

    def read(self, pk, sk):
        return self._get_item(pk, sk)

    def update(self, pk, sk, comment_meta):
        pass