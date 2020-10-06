from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from dynamodb_wrapper.base import DataAlreadyExistsError
from dynamodb_wrapper import User
from .riot_auth import get_riot_id, set_random_icon, get_riot_id_icon
from google_api_wrapper import oauth
import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import background
from google_api_wrapper import drive 

# Create your views here.

# class PostView(APIView):
#     def get(self, request, pk, sk):
#         db = Post(pk, sk).read()
#         if db:
#             return Response(db, status = status.HTTP_200_OK)
#         else:
#             return Response(status = status.HTTP_404_NOT_FOUND)

#     def patch(self, request, pk, sk):
#         res = json.loads(request.body)
#         db = Post(pk, sk)
#         if db.update(res.get('PostTitle'),res.get('PostContent')):
#             return Response(status = status.HTTP_202_ACCEPTED)
#         else:
#             return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
            
#     def post(self, request, pk = None, sk = None):
#         return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)
        
#     def delete(self, request, pk, sk):
#         if Post(pk, sk).delete():
#             return Response(status.HTTP_202_ACCEPTED)
#         else:
#             return Response(status = status.HTTP_406_NOT_ACCEPTABLE)

# class PostListView(APIView):
#     def get(self, request):
#         try:
#             db = Posts()
#             db.add_attributes_to_get('pk','sk','PostData.PostTitle','PostData.Nickname')
#         except:
#             return Response(status = status.HTTP_404_NOT_FOUND)
#         else:
#             return Response(db.go()['Items'], status = status.HTTP_200_OK)

#     def post(self, request):
#         res = json.loads(request.body)
#         print(res)
#         try:
#             Post('testpk0', 'hi').create(res)      
#         except Exception:
#             return Response(status = status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(status = status.HTTP_201_CREATED)

#     def put(self, request):
#         return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)

#     def delete(self, request):
#         return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)

# class CommentListView(APIView):
#     def get(self, request, pk, sk = None):
#         db = CommentList(pk).go()
#         if db:
#             return Response(db, status = status.HTTP_200_OK)
#         else:
#             return Response(status.HTTP_404_NOT_FOUND)

#     def put(self, request, pk, sk = None):
#         return Response(status = status.HTTP_501_NOT_IMPLEMENTED)

#     def patch(self, request, pk, sk):
#         return Response(status = status.HTTP_501_NOT_IMPLEMENTED)

#     def delete(self, reqeust, pk, sk):
#         return Response(status.HTTP_501_NOT_IMPLEMENTED)

# class UserInfoView(APIView):
#     def get(self, request):
#         if request.session['user_sk']:
#             try:
#                 db_request = User(request.session['user_sk'], 'read')
#                 db_request.add_attributes_to_get('User','ClosedUserData')
#                 db_result = db_request.read()
#                 if db_result:
#                     return Response(db_result, status = status.HTTP_200_OK)
#                 else:
#                     return Response(status = status.HTTP_404_NOT_FOUND)
#             except Exception as err:
#                 print(err)
#                 return Response(status = status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(status = status.HTTP_404_NOT_FOUND)            

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

class SignOutView(APIView):
    '''
        모든 로그인 세션 삭제
    '''
    @swagger_auto_schema(
        operation_id = 'Signout',
        responses = {
            200 : '세션 삭제 성공',
            400 : '세션 삭제 실패'
        }
    )
    def get(self, request):
        try:
            request.session.flush()
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            return Response(status = status.HTTP_200_OK)

class UuidSignInView(APIView):
    '''
        UUID를 통한 로그인
    '''

    param_uuid_hint = openapi.Parameter(
        'uuid',
        openapi.IN_QUERY,
        description = 'android uuid',
        type = openapi.TYPE_STRING
    )
    @swagger_auto_schema(
        operation_id = "SignIn_UUID",
        operation_description = "UUID를 통해 계정에 로그인",
        manual_parameters=[param_uuid_hint],
        responses = {
            200 : "로그인 성공",
            400 : "로그인 실패"
        }
    )
    def get(self, request, uuid):
        user_info = User.read(
            pk = 'USER', sk = uuid
        )
        if user_info is None:
            User.create(
                data = {
                    'pk' : 'USER',
                    'sk' : f'uuid#{uuid}',
                    'User' : 'nickname',
                    'ClosedUserData' : {
                        'UserEmail' : '',
                        'UserName' : '',
                        'UserLocale' : '',
                        'RiotID' : []
                }},
                overwrite = False
            ).execute()
        
        request.session['user_sk'] = f'uuid#{uuid}'
        return Response(status = status.HTTP_200_OK)

class GoogleSignInUriView(APIView):
    '''
        구글 Oauth 로그인 페이지 URI를 반환
    '''
    param_redirect_uri_hint = openapi.Parameter(
        'redirect_uri',
        openapi.IN_QUERY,
        description = '로그인 과정이 끝난 후 리다이렉트될 uri',
        type = openapi.TYPE_STRING
    )
    response_redirect_uri = openapi.Schema(
        type = openapi.TYPE_OBJECT,
        propreties = {
            'google_openid_uri' : openapi.Schema(
                type = openapi.TYPE_STRING,
                description = "구글 로그인 URI"
            )
        },
        required = ['google_openid_uri']
    )

    @swagger_auto_schema(
        operation_id = "SignIn_Google_URI",
        operation_description = "구글 로그인 페이지 URI",
        manual_parameters=[param_redirect_uri_hint],
        responses = {
            200 : response_redirect_uri,
            400 : 'URI 받아오기 실패'
        }
    )
    def get(self, request):
        result = {}
        result['google_openid_uri'] = oauth.authorization_url
        return Response(result, status = status.HTTP_200_OK)

# google oauth 웹용으로 쓰던 것
class GoogleSignInView(APIView):
    '''
        구글 Oauth 로그인
        UUID를 통해 로그인 되어 있다면 UUID 로그인 정보가 구글로그인으로 교체되고
        더 이상 해당 UUID 로그인은 불가능해짐

        아무런 파라미터가 없을 경우 구글 로그인 url을 제공함.
    '''
    param_google_token_hint = openapi.Parameter(
        'google_token',
        openapi.IN_QUERY,
        description = 'google oauth 액세스 토큰',
        type = openapi.TYPE_STRING
    )
    
    @swagger_auto_schema(
        operation_id = 'SignIn_Google',
        operation_description = "토큰 방식 및 코드 방식의 구글 Oauth 로그인 처리",
        manual_parameters=[param_google_token_hint],
        responses = {
            200 : "구글 로그인 성공",
            401 : "유효하지 않은 토큰 혹은 코드"
        })
    def get(self, request):
        idinfo = {}
        result = {}
        # get google token and idinfo 
        try:
            if request.GET.get('google_token'):
                idinfo = oauth.verify_id_token(request.GET.get('google_token'))
            elif request.GET.get('state'):
                idinfo = oauth.get_info_from_uri(request.build_absolute_uri())
            else:
                result['google_openid_url'] = oauth.authorization_url
                return Response(result, status = status.HTTP_200_OK)
        except oauth.InvalidTokenError as err:
            return Response(status = status.HTTP_401_UNAUTHORIZED)
        
        # read whether data exists or not
        user_info = None
        user_info = User.read(
            pk = 'USER', sk = f"google#{idinfo['sub']}",
        ).execute()
        if user_info is None and request.GET.get('uuid'):
            user_info = User.read(
                pk = 'USER', sk = f"uuid#{request.GET['uuid']}",
            ).execute()
        
        # create data if not exists
        if user_info is None:
            User.create(
                data = {
                    'pk' : 'USER',
                    'sk' : f'google#{idinfo["sub"]}',
                    'User' : '',
                    'ClosedUserData' : {
                        'UserEmail' : idinfo['email'] if idinfo.get('email') else '',
                        'UserName' : idinfo['name'],
                        'UserLocale' : idinfo['locale'],
                        'RiotID' : []
                }},
                overwrite = False
            ).execute()
        
        # change uuid search key to google search key
        elif 'uuid' in user_info['sk']:
            User.update(
                pk = 'USER', sk = user_info['sk'],
                expressions = [{
                    'utype' : 'SET', 'path' : 'sk', 'value' : f"google#{idinfo['sub']}",
                    'overwrite' : True
                }]
            )
        request.session['user_sk'] = f"google#{idinfo['sub']}"
        request.session['google_access_token'] = idinfo['access_token']
        
        return Response(result, status = status.HTTP_200_OK)

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

        

class GoogleDriveView(APIView):
    @swagger_auto_schema(
        operation_id = 'GoogleDrive_List',
        operation_description = "구글 드라이브 내의 Reloler 영상 조회",
        responses = {
            200 : "조회 성공",
            400 : "조회 실패"
        })
    def get(self, request):
        response = Response()
        try:
            video_list = drive.Drive(request.sessions['google_access_token']).list()
            response.data = video_list
            response.status = status.HTTP_200_OK
            return response
        except Exception:
            response.status = status.HTTP_404_NOT_FOUND
            return response