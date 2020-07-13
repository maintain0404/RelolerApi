from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework import status
from .AWS.post import Post
# Create your views here.


@api_view(['GET', 'POST', 'DELETE'])
def post(request, pk, sk):
    if request.method == 'GET':
        db = Post().read_detail(pk, sk)
        if db:
            return Response(db, status = status.HTTP_200_OK)
        else:
            return Response(status.HTTP_404_NOT_FOUND)
    elif request.method == "POST":
        item = dict()
        item['pk'] = pk
        itme['sk'] = sk
        item['post_meta'] = request.data
        db = Post().create_item(item)
        return Response(status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        Post().delete_item(pk, sk)
        return Response(status.HTTP_202_ACCEPTED)

class CommentsView(APIView):

    def get(self, request, pk):
        

class CommentView(APIView):

