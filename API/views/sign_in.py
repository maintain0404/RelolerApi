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
            200: response_redirect_uri,
            400: 'URI 받기 실패',
            406: '잘못된 redirect_uri 지정'
        }
    )
    def get(self, request):
        result = {}
        try:
            result['google_openid_uri'] = oauth.build_authorization_url(
                request.GET.get("redirect_uri")
            )
        except oauth.InvalidRedirectError:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
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
