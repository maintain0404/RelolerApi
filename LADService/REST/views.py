from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework import status
from .AWS.post import Post
from .AWS.comment import CommentList
from .AWS.video import Video
# Create your views here.


@api_view(['GET', 'POST', 'DELETE'])
def post(request, pk, sk):
    if request.method == 'GET':
        db = Post().read(pk, sk)
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)
    elif request.method == "POST":
        item = dict()
        item['pk'] = pk
        item['sk'] = sk
        Post().create(item, request.data)
        return Response(status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        Post().delete(pk, sk)
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

class VideoView(APIView):
    def get(self, request, pk, sk):
        db = Video().read(pk, sk)
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)