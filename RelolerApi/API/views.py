from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .DynamoDBWrapper.post import Post
from .DynamoDBWrapper.comment import CommentList
from .Oauth import google_auth
from .Oauth import google_open_id
import requests as rq
import google.oauth2.credentials
import google_auth_oauthlib.flow
import jwt

# Create your views here.

class PostView(APIView):
    def get(self, request, pk, sk):
        try:
            db = Post(pk, sk).read()
        except Exception as error:
            print(error)
            return Response(status.HTTP_404_NOT_FOUND)
        else:
            if db:
                return Response(db, status = status.HTTP_200_OK)
            else:
                return Response(status.HTTP_404_NOT_FOUND)

    def update(self, request, pk, sk):
        return Response(status.HTTP_501_NOT_IMPLEMENTED)
            
    # 수정필요
    def post(self, request, pk, sk):
        print(request.body)
        return Response(status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, pk, sk):
        Post(pk, sk).delete()
        return Response(status.HTTP_202_ACCEPTED)

class CommentListView(APIView):
    def get(self, request, pk):
        db = CommentList(pk).go()
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        item = {}
        item['pk'] = pk
        CommentList(pk).put(request.data)
        return Response(status.HTTP_201_CREATED)

    def patch(self, request, pk):
        return Response(status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, reqeust, pk):
        return Response(status.HTTP_501_NOT_IMPLEMENTED)

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
        flow.redirect_uri = 'http://127.0.0.1:8000/api'
        authorization_url, state = flow.authorization_url()
        if request.GET:
            # Oauth 인증과정
            
            flow.fetch_token(authorization_response=request.build_absolute_uri())
            credentials = flow.credentials
            print(dir(credentials))
            print([credentials.token,
                credentials.expired,
                credentials.id_token,
                credentials.scopes,
                credentials.token_uri,
                ])
            
        result = {}
        result['google_openid_url'] = authorization_url
        # result['redirect_url'] = google_auth.authorization_url
        return Response(result, status.HTTP_200_OK)