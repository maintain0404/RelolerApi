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

class ValidationError(Exception):
    def __init__(self):
        super().__init__('Invalid data')

class Validator:
    def __init__(self, data):
        pass

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
            type_prefix = SK.CLIKE
        else:
            raise ValueError('data_type "%s" is not valid data_type' % data_type)
        return type_prefix + datetime.datetime.now().strftime('%Y:%m:%d:%H:%M:%S:%f')

    def is_valid(input_sk):
        return True

class TableBase:
    def __init__(self, table_name = 'Practice'):
        self.table_name = table_name
        self.table = dynamodb.Table(self.table_name)
        self._validators = []

    def _is_valid(self, data, raise_exception = False):
        err = ''
        for validator in self._validators:
            try:
                validator(data)
            except Exception as error:
                err = error
                break
        if err and raise_exception:
            raise ValidationError
        else:
            return True

    def _add_validator(self, func):
        self._validators.append(func)

    def _create_item(self, item):
        if self._is_valid(item):
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
        self._key_condition = {}
        self.attribute_to_get = []
        self._validators = []

    def _is_valid(self, data, raise_exception = False):
        err = ''
        for validator in self._validators:
            try:
                validator(data)
            except Exception as error:
                err = error
                break
        if err and raise_exception:
            raise ValidationError
        else:
            return True
        
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

    def _create_item(self, item):
        if self._is_valid(item):
            self.table.put_item(Item = item)

    def _query(self, pk):
        pk_condition = {'pk':{
            'AttributeValueList' : [pk],
            'ComparisonOperator' : 'EQ'
        }}
        return self.table.query(
            Limit = self._count,
            Select = self._select,
            KeyConditions = pk_condition,
            ScanIndexForward = False
        )

    def _scan(self):
        assert self._key_condition(
            'Class {TableBaseListClass} missing "key_condition" attribute'.format(
                TableBaseListClass = self.__class__.__name__
            )
        )

        return self.table.scan(
            Limit = self._count,
            Select = self._select,
            KeyConditions = self.key_condition,
            ScanIndexForward = False
        )