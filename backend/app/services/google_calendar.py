from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def create_calendar_event(access_token, commitment_text, start_time, end_time):

    credentials = Credentials(token=access_token)

    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": commitment_text,
        "description": "Commitment created via Decision Muscle API",
        "start": {
            "dateTime": start_time,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "UTC"
        }
    }

    event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return event["id"]
