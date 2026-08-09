import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly"
]


def get_calendar_service():
    """
    authenticate the user and return a Google Calendar API service

    OAuth credentials are stored locally in token.json after the
    first successful authentication so that the user does not need
    to log in on every run
    """

    credentials = None

    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES,
        )

    if not credentials or not credentials.valid:

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "credentials.json was not found. "
                    "Google Calendar authentication cannot continue."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )

            credentials = flow.run_local_server(
                port=0
            )

        with open(
            "token.json",
            "w",
            encoding="utf-8",
        ) as token_file:
            token_file.write(
                credentials.to_json()
            )

    service = build(
        "calendar",
        "v3",
        credentials=credentials,
    )

    return service


def fetch_calendar_events(
    days_ahead=7,
    max_results=100,
):
    """
    fetch upcoming events from the user's primary google calendar

    parameters->
    
    days_ahead : int
        number of days ahead to retrieve events

    max_results : int
        maximum number of events returned by the API

    returns->
    
    list
        raw google calendar event objects
    """

    service = get_calendar_service()

    now = datetime.now().astimezone()

    end_time = (
        now
        + timedelta(days=days_ahead)
    )

    response = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end_time.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return response.get(
        "items",
        []
    )


def classify_event_type(title):
    """
    infer a simple workload category from an event title

    this lightweight classification allows Google Calendar events
    to use the same downstream feature extraction pipeline as
    JSON calendar events
    """

    title_lower = title.lower()

    if any(
        keyword in title_lower
        for keyword in [
            "lunch",
            "break",
            "rest",
            "walk",
        ]
    ):
        return "break"

    if any(
        keyword in title_lower
        for keyword in [
            "lecture",
            "class",
            "seminar",
        ]
    ):
        return "lecture"

    if any(
        keyword in title_lower
        for keyword in [
            "coding",
            "programming",
            "study",
            "writing",
            "focus",
            "research",
        ]
    ):
        return "focused_work"

    if "interview" in title_lower:
        return "interview"

    if "presentation" in title_lower:
        return "presentation"

    return "meeting"


def convert_google_event(event):
    """
    convert one google calendar event into MindSync's
    internal event representation

    all day events are currently excluded because MindSync analyses
    timed workload within a working day schedule
    """

    start_data = event.get(
        "start",
        {}
    )

    end_data = event.get(
        "end",
        {}
    )

    start_string = start_data.get(
        "dateTime"
    )

    end_string = end_data.get(
        "dateTime"
    )

    if not start_string or not end_string:
        return None

    start_datetime = datetime.fromisoformat(
        start_string.replace(
            "Z",
            "+00:00",
        )
    )

    end_datetime = datetime.fromisoformat(
        end_string.replace(
            "Z",
            "+00:00",
        )
    )

    local_start = start_datetime.astimezone()
    local_end = end_datetime.astimezone()

    duration_minutes = int(
        (
            local_end
            - local_start
        ).total_seconds()
        / 60
    )

    title = event.get(
        "summary",
        "Untitled Event",
    )

    return {
        "title": title,
        "start": local_start.strftime(
            "%H:%M"
        ),
        "end": local_end.strftime(
            "%H:%M"
        ),
        "type": classify_event_type(
            title
        ),
        "start_time": local_start.replace(
            year=1900,
            month=1,
            day=1,
            tzinfo=None,
        ),
        "end_time": local_end.replace(
            year=1900,
            month=1,
            day=1,
            tzinfo=None,
        ),
        "duration_minutes":
            duration_minutes,
        "date":
            local_start.date().isoformat(),
        "source":
            "google_calendar",
    }


def load_google_calendar(
    days_ahead=7,
):
    """
    load google calendar events and convert them into
    MindSync's internal data format
    """

    raw_events = fetch_calendar_events(
        days_ahead=days_ahead
    )

    converted_events = []

    for raw_event in raw_events:

        converted = convert_google_event(
            raw_event
        )

        if converted is not None:
            converted_events.append(
                converted
            )

    converted_events.sort(
        key=lambda event: (
            event["date"],
            event["start_time"],
        )
    )

    return converted_events


def get_events_for_date(
    events,
    date_string,
):
    """
    return only events belonging to a specified YYYY-MM-DD date
    """

    return [
        event
        for event in events
        if event.get("date")
        == date_string
    ]