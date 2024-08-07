import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

def create_google_calendar_event(appointment):
    # Load service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/calendar']
    )

    # Build the Calendar API service
    service = build('calendar', 'v3', credentials=credentials)

    # Combine date and time into ISO 8601 format
    start_datetime = datetime.datetime.combine(appointment.date, appointment.start_time).isoformat()
    end_datetime = datetime.datetime.combine(appointment.date, appointment.end_time).isoformat()

    # Create an event body
    event = {
        'summary': f'Appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}',
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime,
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
