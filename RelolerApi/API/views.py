from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .DynamoDBWrapper.post import Post
from .DynamoDBWrapper.comment import CommentList
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
