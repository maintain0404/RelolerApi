from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer ,empty
from django.core.validators import RegexValidator
from . import table_base

pk_validator = RegexValidator()
sk_validator = RegexValidator()

class PostSerializer(BaseSerializer):
    def __init__(self, pk, sk = None, data = None, **kwargs):
        instance = dict()
        instance['pk'] = pk
        if sk:
            instance['sk'] = sk
        else:
            instance['sk'] = table_base.current_time()
        super().__init__(instance = instance, data = data)
        self.table = table_base.TableBase('Practice')

    def to_representation(self, instance):
        return instance

    def to_internal_value(self, data):
        return data

    def read(self, instance):
        pk = instance['pk']
        sk = instance['sk']
        return self.table.get_item(pk, sk)

    def create(self, validated_data):
        return self.table.create(validated_data)

    def update(self, instance, data):
        pk = instance['pk']
        sk = instance['sk']
        return self.table.update_item(pk, sk, data)

    def delete(self, instance):
        pk = instance['pk']
        sk = instance['sk']
        self.table.delete_item(pk, sk)