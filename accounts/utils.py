import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from django.conf import settings

TOKEN_PATH = os.path.join(settings.BASE_DIR, 'secrets', 'token.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"The token.json file was not found at {TOKEN_PATH}")
    
    with open(TOKEN_PATH, 'r') as token_file:
        credentials_info = token_file.read()
    
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(credentials_info, SCOPES)
    return credentials

def create_google_calendar_event(appointment):
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)
    
    event = {
        'summary': f'Appointment with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}',
        'start': {
            'dateTime': f"{appointment.date}T{appointment.start_time}",
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': f"{appointment.date}T{appointment.end_time}",
            'timeZone': 'UTC',
        },
        # Additional event details go here
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event
