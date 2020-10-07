from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from dynamodb_wrapper.base import DataAlreadyExistsError
from dynamodb_wrapper import User
from google_api_wrapper import oauth
import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .riot_auth import *

class UserInfoView(APIView):
    userinfo_schema = openapi.Schema(
        type = openapi.TYPE_OBJECT,
        propreties = {
            'nickname' : openapi.Schema(
                type = openapi.TYPE_STRING,
                description = "사용할 닉네임"
            )
        },
        required = ['nickname']
    )
    
    @swagger_auto_schema(
        operation_id = 'UserInfo_GET',
        operation_description = "유저 정보 확인하기, 자신의 계정이라면 추가로 정보가 보임",
        responses = {
            200 : "구글 로그인 성공",
            404 : "존재하지 않는 유저 혹은 기타 에러"
        })
    def get(self, request, logintype, userid, *args, **kargs):
        atbt2get = ['User']
        print(userid)
        if request.session['user_sk'] == f'{logintype}#{userid}':
            atbt2get.append('ClosedUserData')
        try:
            res = User.read(
                pk = 'USER',
                sk = f'{logintype}#{userid}',
                attributes_to_get = atbt2get
            ).execute()
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            return Response(res, status = status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body = userinfo_schema,
        operation_id = 'UserInfo_PUT',
        operation_description = "토큰 방식 및 코드 방식의 구글 Oauth 로그인 처리",
        responses = {
            200 : "구글 로그인 성공",
            401 : "자신이 아닌 다른 유저 정보에 접근",
            404 : "존재하지 않는 유저 혹은 기타 에러"
        })
    def put(self, request, userid, *args, **kargs):
        if request.session['user_sk'] != userid:
            return Response(status = status.HTTP_401_UNAUTHORIZED)

        if request.POST.get('nickname'):
            try:
                User.update(
                    pk = 'USER',
                    sk = userid,
                    expressions = [{
                            'utype' : 'SET',
                            'path' : 'User',
                            'nickname': request.POST.get('nickname'),
                            'overwrite': True
                        }
                    ]
                )
            except Exception as err:
                print(err)
                return Response(status = status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status = status.HTTP_200_OK)
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)


class RiotIDAuthView(APIView):
    '''
        계정의 라이엇 ID 정보
        로그인이 필요함
    '''
    parser_classes = (JSONParser,)
    post_schema = openapi.Schema(
        properties = {'name' : openapi.Schema(
            type = openapi.TYPE_STRING,
            description = '라이엇 계정 닉네임'
        )},
        type = openapi.TYPE_OBJECT
    )
    param_name_hint = openapi.Parameter(
        'name',
        openapi.IN_BODY,
        description = '라이엇 닉네임',
        type = openapi.TYPE_STRING,
    )
    @swagger_auto_schema(
        operation_id = "User_RiotID_LIST",
        operation_description = "계정에 연결된 라이엇 계정 조회",
        responses = {
            200 : "조회 성공",
            400 : "조회 실패",
            401 : "로그인 상태가 아님"
        }
    )
    def get(self, request):
        try:
            print(request.session.items())
            final_res = {}
            if request.session.get('user_sk'):
                res = User.read(
                    pk = 'User',
                    sk = request.session['user_sk'],
                    attributes_to_get = [
                        'ClosedUserData'
                    ]
                ).execute()
                final_res = res['ClosedUserData']['RiotID']
                for idx, v in enumerate(final_res):
                    if not v['Authenticated'] and v['IconID'] == get_riot_id_icon(v['Name']):
                        User.update(
                            pk = 'USER',
                            sk = request.session['user_sk'],
                            expressions = [{  
                                'utype' : 'SET', 
                                'path' : f'ClolsedUserData.RiotID[{idx}].Authenticated',
                                'value' : True
                            }]
                        ).execute()
                        final_res['ClosedUserData']['RiotID'][idx]['Authenticated'] = True
            else:
                return Response(status = status.HTTP_401_UNAUTHORIZED)
                        
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response(final_res, status = status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body = post_schema,
        operation_id = "USER_RiotID_ADD",
        operation_description = "계정에 라이엇 아이디 추가",
        responses = {
            200 : "계정에 새 라이엇 아이디 연결 성공",
            400 : "계정에 새 라이엇 아이디 연결 실패"
        }
    )
    def post(self, request):
        try:
            res = json.loads(request.body)
            riot_id = get_riot_id(res['name'])
            print(riot_id)
            riot_id_dict = dict()
            if riot_id:
                riot_id_dict['Name'] = riot_id['name']
                riot_id_dict['PUUID'] = riot_id['puuid']
                riot_id_dict['IconID'] = set_random_icon(riot_id)
                riot_id_dict['Authenticated'] = False
            else:
                return Response(status = status.HTTP_400_BAD_REQUEST)
            User.update(
                pk = 'USER',
                sk = request.session['user_sk'],
                expressions = [{
                    'utype' : 'LIST_APPEND',
                    'path' : 'ClosedUserData.RiotID',
                    'value' : riot_id_dict
                }]
            ).execute()
            
        except json.JSONDecodeError as err:
            print(err)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except KeyError as err:
            print(err)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response(status = status.HTTP_501_NOT_IMPLEMENTED)
        else:
            return Response(status = status.HTTP_200_OK)
    @swagger_auto_schema(
        request_body = post_schema,
        operation_id = 'User_RiotID_DELETE',
        operation_description = "계정에 연결된 라이엇 아이디 연결 해제",
        responses = {
            200 : "연결 해제 성공",
            400 : "연결 해제 실패"
        }
    )
    def delete(self, request):
        try:
            idx = str(request.GET.get('riot_id_index'))
            User.update(
                pk = 'USER',
                sk = request.session['user_sk'],
                expressions = [{
                    'utype' : 'REMOVE',
                    'path' : f'ClosedUserData.RiotID[{idx}]',
                }]
            ).execute()
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        else: 
            return Response(status = status.HTTP_200_OK)