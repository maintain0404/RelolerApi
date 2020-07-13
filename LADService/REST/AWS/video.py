from .table_base import TableBase, TableBaseList,SK

class Post(TableBase):
    def __init__(self):
        self.table_name = "Practice"
        self.TableIndex = None
        self.ScanIndexForward = False
        super().__init__(self.table_name)

    def _is_valid_meta(self, video_meta):
        pass

    def create(self, pk, video_meta):
        item = dict()
        item['pk'] = pk
        item['sk'] = SK.make('video')
        item['post_meta'] = post_meta
        print(item)

        self._create_item(item)

    def delete(self, pk, sk):
        return self._delete_item(pk, sk)

    def read(self, pk, sk):
        data =  self._get_item(pk, self.SK_POST + sk)
        print(data)
        return data.get('Item')

    def update(self, pk, sk, post_meta):
        pass