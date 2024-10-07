import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarAPIWrapper:
    def __init__(self, token_file='token.json', credentials_file='client_secret.json'):
        load_dotenv()
        self.creds = None
        self.token_file = token_file
        self.credentials_file = credentials_file
        self.service = None

        # Initialize credentials and service
        self.authenticate()

    def authenticate(self):
        """Handles authentication and token refresh"""
        # Load credentials from token.json if available
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials are available, ask the user to log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())
        
        # Initialize the Google Calendar service
        self.service = build('calendar', 'v3', credentials=self.creds)

    def add_event(self, calendar_id='primary', summary='', description='', location='', start_time=None, end_time=None, timezone='UTC'):
        """Adds an event to the user's Google Calendar"""

        if start_time is None or end_time is None:
            raise ValueError("start_time and end_time must be provided")

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            }
        }

        # Call the Google Calendar API to add the event
        event_result = self.service.events().insert(calendarId=calendar_id, body=event).execute()

        print(f"Event created: {event_result.get('htmlLink')}")
        return event_result

    def list_upcoming_events(self, calendar_id='primary', max_results=10):
        """Lists the upcoming events in the user's Google Calendar"""
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId=calendar_id, timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []

        upcoming_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            upcoming_events.append({'start': start, 'summary': event['summary']})

        return upcoming_events