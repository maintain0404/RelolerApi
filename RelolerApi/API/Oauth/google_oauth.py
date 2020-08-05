import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import json

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.
secret_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'google_client_secret.json')
secret_file = json.load(open(secret_path))

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    secret_path,
    scopes = ['openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ],
    state = '12345678910',
)
    
# Indicate where the API server will redirect the user after the user completes
# the authorization flow. The redirect URI is required. The value must exactly
# match one of the authorized redirect URIs for the OAuth 2.0 client, which you
# configured in the API Console. If this value doesn't match an authorized URI,
# you will get a 'redirect_uri_mismatch' error.
flow.redirect_uri = 'http://127.0.0.1:8000/api/signup/google'

# Generate URL for request to Google's OAuth 2.0 server.
# Use kwargs to set optional request parameters.
authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

def verify_id_token(credentials):
    idinfo = id_token.verify_oauth2_token(credentials, 
        requests.Request(),
        secret_file['web']['client_id']
    )
    return idinfo

def verify_id_token_form_uri(uri):
    flow.fetch_token(authorization_response=uri)
    return verify_id_token(flow.credentials)