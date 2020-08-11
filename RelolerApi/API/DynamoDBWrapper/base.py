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

class DataAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Data is already exists.")

class SK:
    VIDEO = "vid#"
    POST = "pst#"
    COMMENT = "cmt#"
    PLIKE = "plk#"
    CLIKE = "clk#"

def make_new_sk(data_type : str, time_code = None):
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

def sk_is_valid(input_sk):
    return True

class BaseItemWrapper:
    def __init__(self, pk = None, sk = None, table_name = 'Practice', index_name = None, 
        request_type = "read", new_data = None):
        self.table_name = table_name
        self.table = dynamodb.Table(self.table_name)
        self.index_name = index_name
        self._attributes_to_get = []
        self.request_type = request_type
        self.pk = pk
        self.sk = sk
        self._validators = []
        self._data = {}
        self._update_expression = ''
        self._update_values = {}
        self.update_type = 'SET'

    @property
    def attributes_to_get(self):
        assert (self.request_type == 'read' ,
            "request_type must be 'read' to use attributes_to_get"
        )
        return self._attributes_to_get

    def add_attributes_to_get(self, *args):
        assert (self.request_type == 'read' ,
            "request_type must be 'read' to use attributes_to_get"
        )
        for attribute in args:
            self._attributes_to_get.append(attribute)

    def update_expression(self, utype, path, value = None, overwrite = False):
        # 26개 이하로 요청할것
        value_key = f':{chr(len(self._update_values) + 65)}'
        self.update_type = utype
        if utype == 'SET':
            self._update_values[value_key] = value
            uexp = f'SET {path} = {value_key}'
        elif utype == 'LIST_APPEND':
            self._update_values[value_key] = [value]
            uexp = f'SET {path} = list_append({path}, {value_key})'
        elif utype == 'ADD_NUMBER':
            self._update_values[value_key] = value
            uexp = f'ADD {path} {value_key}' 
        elif utype == 'REMOVE':
            uexp = f'REMOVE {path}'
        elif utype == 'DELETE':
            uexp = f'DELETE {path}'
        self._update_expression = uexp
        
    def to_internal(self, new_data):
        self._data = new_data

    def data_is_valid(self, raise_exception = False):
        assert (self.request_type == "create" or 'update', 
            "request_type must be 'create' or update to use data"
        )
        err = ''
        for validator in self._validators:
            try:
                validator(self._data)
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
            try:
                result = self.table.put_item(
                    Item = self._data,
                    ConditionExpression = And(Attr('sk').not_exists(), Attr('pk').ne(self.pk))
                )
            except Exception as err:
                if err.__class__.__name__ == 'ConditionalCheckFailedException':
                    raise DataAlreadyExistsError
                else:
                    raise err
            else:
                return result.get('Item')
        else:
            return False

    def read(self):
        # Item에는 순전히 결과만 포함되어 있음, 추가 정보를 나중에 수정할 것
        final_func = functools.partial(self.table.get_item,
            Key = {
                'pk' : self.pk,
                'sk' : self.sk
            }
        )
        if self.attributes_to_get:
            projection_expression = ', '.join(self.attributes_to_get)
            final_func.keywords['ProjectionExpression'] = projection_expression
        
        result = final_func()
        print(result)
        return result.get('Item')

    def update(self):
        final_func = functools.partial( self.table.update_item,
            Key = {
                'pk' : self.pk,
                'sk' : self.sk
            },
            UpdateExpression = self._update_expression
        )
        if self.update_type not in ('DELETE', 'REMOVE'):
            final_func.keywords['ExpressionAttributeValues'] = self._update_values
        print(self._update_values)
        print(self._update_expression)
        print(final_func.keywords)
        result = final_func()
    
        return result.get('Item')
        
    def delete(self):
        # 지워도 되는지 검증하는 절차가 필요하지 않을까?\
        try:
            result = self.table.delete_item(
                Key = {
                    'pk' : self.pk,
                    'sk' : self.sk
                }
            )
        except Exception as err:
            print('error on delete')
            print(err)
            return False
        else:
            return True

    def go(self):
        if self.request_type == "read":
            return self.read()
        elif self.request_type == 'create':
            return self.create()
        elif self.request_type == 'update':
            return self.update()
        elif self.request_type == 'delete':
            return self.delete()

class QueryScanSetterMixin:
    def __init__(self, table_name="Practice", count = 30):
        self.table_name = table_name
        self.table = dynamodb.Table(table_name)
        self.count = count
        self.exclusive_start_key = None
        self._attributes_to_get = []
        self.filter_expression = None

    @property
    def attributes_to_get(self):
        return self._attributes_to_get

    def add_attributes_to_get(self, *args):
        for attribute in args:
            self._attributes_to_get.append(attribute)

class BaseQueryWrapper(QueryScanSetterMixin):
    def __init__(self, pk, table_name = "Practice", count = 30):
        super().__init__(table_name, count)
        self.pk = pk

    def go(self):
        final_query_func = functools.partial(self.table.query,
            Limit = self.count,
            KeyConditionExpression = self.pk,
            ScanIndexForward = False,
            ConsistentRead = False # True로 바꾸면 실시간 반영이 더 엄밀해짐
        )
        if self.filter_expression:
            final_query_func.keywords['FilterExpression'] = self.filter_expression
        
        if self.exclusive_start_key:
            final_query_func.keywords['ExclusiveStartKey'] = self.exclusive_start_key

        if self.attributes_to_get:
            projection_expression = ', '.join(self.attributes_to_get)
            final_query_func.keywords['Select'] = 'SPECIFIC_ATTRIBUTES'
            final_query_func.keywords['ProjectionExpression'] = projection_expression
        
        # 에러 핸들링 구현 필요
        try:
            result = final_query_func()
        except Exception as err:
            return None
        else:
            return result

class BaseScanWrapper(QueryScanSetterMixin):
    def __init__(self, table_name = "Practice", count = 30):
        super().__init__(table_name, count)

    def go(self):
        final_scan_func = functools.partial(self.table.scan,
            Limit = self.count,
            ConsistentRead = False # True로 바꾸면 실시간 반영이 더 엄밀해짐
        )
        if self.filter_expression:
            final_scan_func.keywords['FilterExpression'] = self.filter_expression
        
        if self.exclusive_start_key:
            final_scan_func.keywords['ExclusiveStartKey'] = self.exclusive_start_key

        if self.attributes_to_get:
            projection_expression = ', '.join(self.attributes_to_get)
            final_scan_func.keywords['Select'] = 'SPECIFIC_ATTRIBUTES'
            final_scan_func.keywords['ProjectionExpression'] = projection_expression
        
        # 에러 핸들링 구현 필요
        try:
            result = final_scan_func()
        except Exception as err:
            print(err)
            return None
        else:
            return result