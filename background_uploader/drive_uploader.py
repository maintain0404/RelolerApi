import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .run import app


def build_service_by_access_token(token):
    creds = Credentials(token)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise ValueError("Invalid Access Token")

    return build('drive', 'v3', credentials = creds)

def drive_upload(service, filepath):
    # 파일에 맞게 mimetype은 세팅해줄 필요가 있음
    # 동영상만 올릴 것을 가정하기 때문에 webm 썼다
    media = MediaFileUpload(filepath, mimetype='video/webm',
        chunksize = -1, resumable = True)
    # 역시 파일에 맞게 이름 지정할 것
    # 이 속성으로 폴더 및 각종 옵션 지정 가능 / 폴더 옵션은 이유 불명으로 미작동
    # 참고 https://developers.google.com/drive/api/v3/reference/files/create
    request_body = {'name':'background.webm', 
        #'parents':[폴더 아이디]
    }
    # fields 속성을 통해 반환값을 지정할 수 있는 듯한데 더 알아봐야 함
    upload_request = service.files().create(body = request_body, media_body = media, fields = 'id')
    response = None
    error = None
    # 업로드가 1청크로 바로 끝나서 더 큰 것에 대한 검증이 필요함
    while response is None:
        status, response = upload_request.next_chunk()
        if response is not None:
            print('success')
        else:
            print('failed')



@app.task
def upload_test_video(access_token):
    try:
        service = build_service_by_access_token(access_token)
        drive_upload(service,
            '/home/taein/projects/RelolerApi/background.webm')
        return f"{access_token}  clear"
    except Exception as err:
        print(str(err))
        return str(err)
