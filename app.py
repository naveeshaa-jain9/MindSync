from src.data_loader import load_calendar_from_json


def main():
    calendar = load_calendar_from_json("data/sample_calendar.json")

    print("MindSync")
    print("=" * 50)
    print(f"Calendar date: {calendar['date']}")
    print()

    for event in calendar["events"]:
        print(
            f"{event['start']} - {event['end']} | "
            f"{event['title']} | "
            f"{event['type']} | "
            f"{event['duration_minutes']} mins"
        )


if __name__ == "__main__":
    main()
