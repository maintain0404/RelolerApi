import json
import boto3
import os
import datetime

settings = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'access_key.json')))

dynamodb = boto3.resource('dynamodb',
    region_name = 'ap-northeast-2', # 서울
    aws_access_key_id = settings['AWS']['Access Key ID'],
    aws_secret_access_key = settings['AWS']['Security Access Key'],
)   

class SK:
    VIDEO = "vid#"
    POST = "pst#"
    COMMENT = "cmt#"
    PLIKE = "plk#"
    CLIKE = "clk#"

    def make(data_type : str, time_code = None):
        if data_type == 'video':
            type_prefix = SK.VIDEO
        elif data_type == 'post':
            type_prefix = SK.POST
        elif data_type == 'comment':
            type_prefix = SK.COMMENT
        elif data_type == 'post_like':
            type_prefix = SK.PLIKE
        elif data_type == 'comment_like':
            type_prefix - SK.CLIKE
        else:
            raise ValueError('data_typa "%s" is not valid data_type' % data_type)
        if SK.is_valid(time_code):
            return type_prefix + time_code
        else:
            return type_prefix + datetime.datetime.now().strftime('%Y:%m:%d:%H:%M:%s:%f')

    def is_valid(input_sk):
        return True

class TableBase:
    def __init__(self, table_name = 'Practice'):
        self.table_name = table_name
        self.table = dynamodb.Table(self.table_name)

    def _is_valid(self):
        pass

    def _create_item(self, item):
        self.table.put_item(Item = item)

    def _get_item(self, pk, sk):
        # Item에는 순전히 결과만 포함되어 있음, 추가 정보를 나중에 수정할 것
        result = self.table.get_item(
            Key = {
                'pk' : pk,
                'sk' : sk
            }
        )
        return result

    def _delete_item(self, pk, sk):
        self.table.delete(
            Key = {
                'pk' : pk,
                'sk' : sk
            }
        )

    def _update_item(self, pk, sk, item):
        self.table.update_itme(
            Key = {
                'pk' : pk,
                'sk' : sk
            },
            Item = item
        )

class TableBaseList:
    def __init__(self, table_name="Practice"):
        self.table_name = table_name
        self.table = dynamodb.Table(table_name)
        self._count = 30
        self._select = 'ALL_ATTRIBUTES'
        self.attribute_to_get = []
        
    @property 
    def count(self):
        return self._count

    @count.setter
    def count(self, number):
        self._count = number

    @property
    def key_condition(self):
        return self._key_condition

    @property
    def atttibutes_to_get(self):
        pass

    def add_key_condition(self, attribute_name, values_to_compare : list, operator : str):
        self._key_condition[attribute_name] = {
            'AttributeValueList' : values_to_compare,
            'ComparisonOperator' : operator
        }

    def _query(self, pk):
        assert self.key_condition(
            'Class {TableBaseListClass} missing "key_condition" attribute'.format(
                TableBaseListClass = self.__class__.__name__
            )
        )
        pk_condition = {'pk':{
            'AttributeValueList' : [pk],
            'ComparitonOperator' : 'EQ'
        }}
        temp = self.key_condition.copy()
        temp.update(pk_condition)
        return self.table.query(
            Limit = self._count,
            Select = self.select,
            KeyConditions = temp,
            ScanIndexForward = False
        )
        

    def _scan(self):
        assert self.key_condition(
            'Class {TableBaseListClass} missing "key_condition" attribute'.format(
                TableBaseListClass = self.__class__.__name__
            )
        )

        return self.table.scan(
            Limit = self._count,
            Select = self.select,
            KeyConditions = self.key_condition,
            ScanIndexForward = False
        )