import pickle
import os
import httplib2
import random
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

CLIENT_SECRETS_PATH = "C:\Projects\AutoLoLDirector\youtube_uploader\google_client_secret.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MAX_RETRIES = 2


def build_authenticated_youtube_service(creds):
    if not creds.valid:
        if not creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_PATH, [YOUTUBE_UPLOAD_SCOPE]
            )
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials = creds)

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        # except HttpError as e:
        #     if e.resp.status in RETRIABLE_STATUS_CODES:
        #         error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
        #                                                                 e.content)
        #     else:
        #         raise
        except Exception as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

def initialize_upload(youtube):
    body=dict(
        snippet=dict(
            title= '시범제목',
            description= '시범설명',
            tags= None,
            categoryId= 22
        ),
        status=dict(
            privacyStatus= 'private'
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload('C:\Projects\AutoLoLDirector\youtube_uploader\karthus_pentakill.webm', chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)
