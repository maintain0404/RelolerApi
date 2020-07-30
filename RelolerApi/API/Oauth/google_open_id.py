import hashlib
import json
import os
import base64

gcs_json = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'google_client_secret.json')))

def openid_login_url():
    client_id = gcs_json['web']['client_id']
    response_type = 'code'
    scope = 'openid email profile'
    redirect_uri = 'http://127.0.0.1:8000/api'
    nonce = '0394852-3190485-2490358'
    # Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    # Set the client ID, token state, and application name in the HTML while
    # serving it.
    url = ['https://accounts.google.com/o/oauth2/v2/auth?',
        'response_type=' , response_type ,'&',
        'client_id=' , client_id , '&',
        'scope=' , scope , '&',
        'redirect_uri=' , redirect_uri , '&',
        'nonce' , '0394852-3190485-2490358' , '&']
    url = ''.join(url)
    return url

# def jwt_decode(jwt_string):
#     header, payload, signature = jwt_string.parse('.')
#     for x in ['','=','==']:
#         try:
#             base64.b64decode(header +)