import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'
    
    if os.path.exists(token_path):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    return creds

def create_google_calendar_event(event_details):
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    event = service.events().insert(calendarId='primary', body=event_details).execute()
    return event
