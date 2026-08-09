from src.data_loader import load_calendar_from_json
from src.features import extract_calendar_features


def main():
    calendar = load_calendar_from_json(
        "data/sample_calendar.json"
    )

    print("MindSync")
    print("=" * 50)
    print(f"Calendar date: {calendar['date']}")
    print()

    print("CALENDAR EVENTS")
    print("-" * 50)

    for event in calendar["events"]:
        print(
            f"{event['start']} - {event['end']} | "
            f"{event['title']} | "
            f"{event['type']} | "
            f"{event['duration_minutes']} mins"
        )

    features = extract_calendar_features(
        calendar["events"]
    )

    print()
    print("EXTRACTED FEATURES")
    print("-" * 50)

    for feature_name, value in features.items():
        print(f"{feature_name}: {value}")


if __name__ == "__main__":
    main()