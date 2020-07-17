from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework import status
from .DynamoDBWrapper.post import Post
from .DynamoDBWrapper.comment import CommentList
from .DynamoDBWrapper.video import Video
# Create your views here.

class PostView(APIView):
    def get(self, request, pk):
        db = Post(pk, sk).read()
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)
            
    # 수정필요
    def post(self, request, pk):
        
        return Response(status.HTTP_201_CREATED)

    def delete(self, request, pk):
        Post(pk, sk).delete()
        return Response(status.HTTP_202_ACCEPTED)

class CommentListView(APIView):
    def get(self, request, pk):
        db = CommentList().read(pk)
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        item = {}
        item['pk'] = pk
        CommentList().create(pk, request.data)
        return Response(status.HTTP_201_CREATED)

class PostListView(APIView):

class VideoView(APIView):
    def get(self, request, pk, sk):
        db = Video().read(pk, sk)
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)