from .table_base import TableBase


class User(TableBase):
    def __init__(self):
        super().__init__('User')
        self.index = 'UserIndex'

    def create(self, user_meta):
        pass

    def read(self, pk, sk):

    def update(self, pk, sk, user_meta):

    def delete(self, pk, sk):