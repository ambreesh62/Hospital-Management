import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

def create_google_calendar_event(appointment):
    # Use the credentials to build the Google Calendar service
    credentials = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/calendar']
    )

    service = build('calendar', 'v3', credentials=credentials)

    # Create an event body
    event = {
        'summary': f'Appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}',
        'start': {
            'dateTime': f'{appointment.date}T{appointment.start_time}',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': f'{appointment.date}T{appointment.end_time}',
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': appointment.doctor.email},
            {'email': appointment.patient.email},
        ],
    }

    # Insert the event into the calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event
