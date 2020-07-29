import json
import boto3
from boto3.dynamodb.conditions import *
import os
import datetime
import functools

settings = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'access_key.json')))

dynamodb = boto3.resource('dynamodb',
    region_name = 'ap-northeast-2', # 서울
    aws_access_key_id = settings['AWS']['Access Key ID'],
    aws_secret_access_key = settings['AWS']['Security Access Key'],
)   

class ValidationError(Exception):
    def __init__(self):
        super().__init__('Invalid data')

class InvaildPrimaryKeyError(Exception):
    def __init__(self):
        super().__init__("PK and SK must exist or must not exist simultaneously")

class NotImplementedError(execption):
    def __init__(self, error_msg):
        super().__init__(error_msg)

class Validator:
    def __init__(self, data):
        pass

class SK:
    VIDEO = "vid#"
    POST = "pst#"
    COMMENT = "cmt#"
    PLIKE = "plk#"
    CLIKE = "clk#"

    def make_new(data_type : str, time_code = None):
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

class BaseItemWrapper:
    def __init__(self, pk, sk, table_name = 'Practice', index_name = None):
        self.table_name = table_name
        self.table = dynamodb.Table(self.table_name)
        self.index_name = index_name
        self.pk = pk
        self.sk = sk
        self._validators = []
        self._data = {}
        self._data['pk'] = self.pk
        self._data['sk'] = self.sk

    @property
    def data(self):
        return self._data

    def data_is_valid(self, raise_exception = False):
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

    def add_validator(self, func):
        self._validators.append(func)

    def create(self):
        if self.data_is_valid():
            result = self.table.put_item(
                Key = {
                    'pk' : self.pk,
                    'sk' : self.sk
                },
                Item = self._data,
                ConditionExpression = And(Attr('sk').not_exists(), Attr('pk').ne(self.pk))
            )

    def read(self):
        # Item에는 순전히 결과만 포함되어 있음, 추가 정보를 나중에 수정할 것
        result = self.table.get_item(
            Key = {
                'pk' : self.pk,
                'sk' : self.sk
            },
        )
        return result.get('Item')

    def update(self, attribute_names, values):
        raise NotImplementedError("update must be implemented")

    def delete(self):
        # 지워도 되는지 검증하는 절차가 필요하지 않을까?
        result = self.table.delete_item(
            Key = {
                'pk' : self.pk,
                'sk' : self.sk
            }
        )

class BaseQueryWrapper:
    def __init__(self, pk, table_name="Practice", count = 30):
        self.pk = pk
        self.table_name = table_name
        self.table = dynamodb.Table(table_name)
        self.count = count
        self.exclusive_start_key = ''
        self._attributes_to_get = []
        self.filter_expression = None

    @property
    def attributes_to_get(self):
        return self._attributes_to_get

    def add_attributes_to_get(self, *args):
        for attribute in args:
            self._attributes_to_get.append(attribute)

    def go(self):
        if self.filter_expression:
            query_partial = functools.partial(
                self.table.query,
                Limit = self.count,
                KeyConditionExpression = Key('pk').eq(self.pk),
                ScanIndexForward = False,
                ConsistentRead = False, # True로 바꾸면 DB의 실시간 반영이 더 엄밀해짐
            )
        else:
            query_partial = functools.partial(
                self.table.query,
                Limit = self.count,
                KeyConditionExpression = Key('pk').eq(self.pk),
                ScanIndexForward = False,
                FilterExpression = self.filter_expression,
                ConsistentRead = False, # True로 바꾸면 DB의 실시간 반영이 더 엄밀해짐
            )
        if not self.attributes_to_get:
            if self.exclusive_start_key:
                return query_partial(
                    ExclusiveStartKey = self.exclusive_start_key
                )
            else:
                return query_partial()
        else:
            # 인덱스 오류 안나게 수정 필요
            projection_expression = self._attributes_to_get[0]
            for x in self._attributes_to_get[1:]:
                projection_expression = ', ' + projection_expression

            if self.exclusive_start_key:
                return query_partial(
                    Select = 'SPECIFIC_ATTRIBUTES',
                    ProjectionExpression = projection_expression,
                    ExclusiveStartKey = self.exclusive_start_key
                )
            else:
                return query_partial(
                    Select = 'SPECIFIC_ATTRIBUTES',
                    ProjectionExpression = projection_expression
                )
