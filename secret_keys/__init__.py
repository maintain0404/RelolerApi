import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

riot_secret_file = open(os.path.join(current_dir, 'riot_secret_key.json'))
riot_secret_key = json.load(riot_secret_file)['key']

aws_secret_file = open(os.path.join(current_dir, 'aws_access_key.json'))
aws_secret = json.load(aws_secret_file)

google_client_secret_path = os.path.join(current_dir, 'google_client_secret.json')
google_client_secret_file = json.load(open(google_client_secret_path))
google_client_id = google_client_secret_file['web']['client_id']
google_redirect_uris = google_client_secret_file['web']['redirect_uris']

django_secret_key = '2k^%70kv(+_688^b^94^v-8f9vwp#nne)40n7*1k^6v!in0zc-'