from .base import *
import jsonschema
import os

schema_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schemas')
post_input_schema_file = open(os.path.join(schema_directory, 'post_input.json'), encoding = 'UTF-8')
post_input_schema = json.loads(post_input_schema_file.read())
post_input_validator = functools.partial(jsonschema.validate, 
    schema = post_input_schema
    )
class Post(BaseItemWrapper):
    def __init__(self, pk = None, sk = None):
        super().__init__(pk = pk, sk = "pst#" + sk)


    ## 데이터 요청 세팅함수
    def to_internal(self, new_data):
        try:
            post_input_validator(instance = new_data)
        except jsonschema.exceptions.ValidationError:
            return False
        else:
            self._data['pk'] = 'testpk0'
            self._data['sk'] = SK.make_new('post')
            self._data['PostPK'] = 'testpk0'
            self._data['User'] = 'test_user'
            self._data['PostData'] = new_data
            return True        
    
    def update(self, title, content):
        self.reqeust_type = 'update'
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

class Posts(BaseScanWrapper):
    def __init__(self):
        super().__init__()