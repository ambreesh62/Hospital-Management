import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('path_to_client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds
