import json
from datetime import datetime
from pathlib import Path


def load_calendar_from_json(file_path):
    """
    Load calendar events from a JSON file

    Parameters
    ----------
    file_path : str
        path to the calendar JSON file

    Returns
    -------
    dict
        calendar data containing the date and parsed events
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Calendar file not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        calendar_data = json.load(file)

    if "events" not in calendar_data:
        raise ValueError("Calendar JSON must contain an 'events' field.")

    parsed_events = []

    for event in calendar_data["events"]:
        required_fields = {"title", "start", "end", "type"}

        if not required_fields.issubset(event):
            missing = required_fields - set(event)
            raise ValueError(
                f"Event '{event.get('title', 'Unknown')}' "
                f"is missing fields: {missing}"
            )

        start_time = datetime.strptime(event["start"], "%H:%M")
        end_time = datetime.strptime(event["end"], "%H:%M")

        if end_time <= start_time:
            raise ValueError(
                f"End time must be after start time for '{event['title']}'."
            )

        duration_minutes = int(
            (end_time - start_time).total_seconds() / 60
        )

        parsed_events.append(
            {
                "title": event["title"],
                "start": event["start"],
                "end": event["end"],
                "type": event["type"],
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
            }
        )

    parsed_events.sort(key=lambda event: event["start_time"])

    return {
        "date": calendar_data.get("date"),
        "events": parsed_events,
    }