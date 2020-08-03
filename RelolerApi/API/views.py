from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .DynamoDBWrapper.post import Post, Posts
from .DynamoDBWrapper.comment import CommentList
from .DynamoDBWrapper.schema_validator import *
from .Oauth import google_auth
from .Oauth import google_open_id
import requests as rq
from google.oauth2 import id_token
from google.auth.transport import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
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

class RiotIDAuthView(APIView):
    pass

        
# google oauth 웹용으로 쓰던 것
class OauthView(APIView):
    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            google_auth.secret_path,
            scopes=['openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            state = '12345678910',
        ) # 이 영역을 지정된 링크의 리스트로 넣음으로서 다른 권한에 접근가능
        flow.redirect_uri = 'http://127.0.0.1:8000/api/signup/google'
        authorization_url, state = flow.authorization_url()
        if request.GET:
            # Oauth 인증과정
            
            flow.fetch_token(authorization_response=request.build_absolute_uri())
            credentials = flow.credentials
            print(dir(credentials))
            idinfo = id_token.verify_oauth2_token(credentials.id_token, requests.Request(),
                "1048634699120-krqt8pi3vnt0b5b6j76jhfjdmqdu2uqa.apps.googleusercontent.com")
            print(idinfo)
            
        result = {}
        result['google_openid_url'] = authorization_url
        # result['redirect_url'] = google_auth.authorization_url
        return Response(result, status.HTTP_200_OK)