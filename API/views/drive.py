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
