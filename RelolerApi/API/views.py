from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .DynamoDBWrapper.base import DataAlreadyExistsError
from .DynamoDBWrapper.post import Post, Posts
from .DynamoDBWrapper.comment import CommentList
from .DynamoDBWrapper.user import User
from .DynamoDBWrapper.riot_auth import get_riot_id, set_random_icon
from .DynamoDBWrapper.schema_validator import *
from .Oauth import google_oauth
import json

# Create your views here.

class PostView(APIView):
    def get(self, request, pk, sk):
        db = Post(pk, sk).read()
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status = status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, sk):
        res = json.loads(request.body)
        db = Post(pk, sk)
        if db.update(res.get('PostTitle'),res.get('PostContent')):
            return Response(status = status.HTTP_202_ACCEPTED)
        else:
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
            
    def post(self, request, pk = None, sk = None):
        return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def delete(self, request, pk, sk):
        if Post(pk, sk).delete():
            return Response(status.HTTP_202_ACCEPTED)
        else:
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)

class PostListView(APIView):
    def get(self, request):
        try:
            db = Posts()
            db.add_attributes_to_get('pk','sk','PostData.PostTitle','PostData.Nickname')
        except:
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            return Response(db.go()['Items'], status = status.HTTP_200_OK)

    def post(self, request):
        res = json.loads(request.body)
        print(res)
        if post_is_valid(res):
            Post('testpk0', 'hi').create(res)
            return Response(status = status.HTTP_201_CREATED)
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request):
        return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)

class CommentListView(APIView):
    def get(self, request, pk, sk = None):
        db = CommentList(pk).go()
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, sk = None):
        item = {}
        item['pk'] = pk
        CommentList(pk).create(request.data)
        return Response(status.HTTP_201_CREATED)

    def patch(self, request, pk, sk):
        return Response(status = status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, reqeust, pk, sk):
        return Response(status.HTTP_501_NOT_IMPLEMENTED)

class UserInfoView(APIView):
    def get(self, request):
        if request.session['sub']:
            try:
                db_request = User('google#' + request.session['sub'], 'read')
                db_request.add_attributes_to_get('User','ClosedUserData')
                db_result = db_request.read()
                if db_result:
                    return Response(db_result, status = status.HTTP_200_OK)
                else:
                    return Response(status = status.HTTP_404_NOT_FOUND)
            except Exception as err:
                print(err)
                return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status = status.HTTP_404_NOT_FOUND)            

class RiotIDAuthView(APIView):
    def get(self, request):
        try:
            print(request.session.items())
            final_res = {}
            if request.session.get('sub'):
                user_request = User('google#' + request.session['sub'])
                user_request.add_attributes_to_get('ClosedUserData')
                res = user_request.read()
                print(res)
                final_res = res['ClosedUserData']['RiotID']
                 
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response(final_res, status = status.HTTP_200_OK)

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
            user_request = User("google#" + request.session['sub'], request_type = 'update')
            user_request.set_update_expression('SET ClosedUserData.RiotID = list_append(ClosedUserData.RiotID, :RID)')
            user_request.add_update_values(':RID', riot_id_dict)
            user_request.update()

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

    def put(self, request):
        return Response(status = status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request):
        return Response(status = status.HTTP_501_NOT_IMPLEMENTED)

class SignOutView(APIView):
    def get(self, request):
        try:
            final_rspn = Response()
            request.session.flush()
            final_rspn.delete_cookie()
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            return Response(status = status.HTTP_200_OK)

# google oauth 웹용으로 쓰던 것
class GoogleSignInView(APIView):
    def get(self, request):
        print(request.COOKIES)
        print(request.session.session_key)
        
        idinfo = {}
        result = {}
        try:
            if request.GET.get('id_token'):
                idinfo = google_oauth.verify_id_token(request.GET.get('id_token'))
                user_request = User('create')
                user_request.to_internal(idinfo)
                user_request.create() 
            elif request.GET.get('state'):
                # Oauth 인증과정
                idinfo = google_oauth.verify_id_token_form_uri(request.build_absolute_uri())
                user_request = User('create')
                user_request.to_internal(idinfo)
                user_request.create()            
                print(idinfo)
            else:
                result['google_openid_url'] = google_oauth.authorization_url
        except DataAlreadyExistsError as err:
            print(err)
            request.session['user_sk'] = '#google' + idinfo['sub']
        except Exception as err:
            print(err)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        finally:
            return Response(result, status = status.HTTP_200_OK)
