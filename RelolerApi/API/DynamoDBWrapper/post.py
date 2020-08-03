from .base import *
import jsonschema
import os


class Post(BaseItemWrapper):
    def __init__(self, pk, sk):
        super().__init__(pk, "pst#" + sk)

    def update(self, title, content):
        expression_attribute_values = {
            ":PT" : title,
            ":PC" : content
        }
        update_expression = "SET PostData.PostTitle = :PT, PostData.PostContent = :PC"
        try:
            result = self.table.update_item(
                Key = {
                    'pk' : self.pk,
                    'sk' : self.sk
                },
                ExpressionAttributeValues = expression_attribute_values,
                UpdateExpression = update_expression
            )
        except Exception as err:
            print(err)
            return None
        else:
            return result.get('Item')

    def create(self, new_data):
        data_to_create = {}
        data_to_create['PostData'] = new_data
        data_to_create['User'] = 'test_user'
        data_to_create['PostPK'] = 'testpk0'
        data_to_create['pk'] = 'testpk0'
        data_to_create['sk'] = SK.make_new('post')
        try:
            result = self.table.put_item(
                Item = data_to_create,
                ConditionExpression = And(Attr('sk').not_exists(), Attr('pk').ne(self.pk))
            )
        except Exception

class Posts(BaseScanWrapper):
    def __init__(self):
        super().__init__()