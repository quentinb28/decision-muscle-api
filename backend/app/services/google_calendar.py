from dotenv import load_dotenv
import os
from fastapi import Depends
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.auth import get_current_user

from models.user import User

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


def create_calendar_event(
        user,
        commitment_text, 
        start_time, 
        end_time
    ):

    credentials = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )

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
