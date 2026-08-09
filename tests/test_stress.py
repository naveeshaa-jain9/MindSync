from datetime import datetime
from src.features import extract_calendar_features
from src.stress_engine import calculate_stress_risk


def make_event(title, start, end, event_type):
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")

    return {
        "title": title,
        "start": start,
        "end": end,
        "type": event_type,
        "start_time": start_time,
        "end_time": end_time,
        "duration_minutes": int(
            (end_time - start_time).total_seconds() / 60
        ),
    }


SCENARIOS = {
    "Light Day": [
        make_event(
            "Morning Meeting",
            "09:00",
            "09:45",
            "meeting",
        ),
        make_event(
            "Focused Work",
            "11:00",
            "12:00",
            "focused_work",
        ),
        make_event(
            "Lunch",
            "13:00",
            "14:00",
            "break",
        ),
    ],

    "Moderate Day": [
        make_event(
            "Team Meeting",
            "09:00",
            "10:00",
            "meeting",
        ),
        make_event(
            "Focused Work",
            "10:30",
            "12:00",
            "focused_work",
        ),
        make_event(
            "Lunch",
            "12:30",
            "13:00",
            "break",
        ),
        make_event(
            "Lecture",
            "13:30",
            "14:30",
            "lecture",
        ),
        make_event(
            "Project Meeting",
            "15:00",
            "16:00",
            "meeting",
        ),
    ],

    "Back-to-Back Day": [
        make_event(
            "Meeting 1",
            "09:00",
            "10:00",
            "meeting",
        ),
        make_event(
            "Meeting 2",
            "10:00",
            "11:00",
            "meeting",
        ),
        make_event(
            "Meeting 3",
            "11:00",
            "12:00",
            "meeting",
        ),
        make_event(
            "Meeting 4",
            "12:00",
            "13:00",
            "meeting",
        ),
        make_event(
            "Meeting 5",
            "13:00",
            "14:00",
            "meeting",
        ),
    ],

    "Context-Switch Heavy": [
        make_event(
            "Team Meeting",
            "09:00",
            "09:45",
            "meeting",
        ),
        make_event(
            "Coding Session",
            "10:00",
            "11:00",
            "focused_work",
        ),
        make_event(
            "Lecture",
            "11:15",
            "12:15",
            "lecture",
        ),
        make_event(
            "Client Meeting",
            "12:30",
            "13:15",
            "meeting",
        ),
        make_event(
            "Report Writing",
            "13:30",
            "14:30",
            "focused_work",
        ),
        make_event(
            "Presentation",
            "14:45",
            "15:30",
            "presentation",
        ),
    ],

    "Recovery-Rich Day": [
        make_event(
            "Meeting",
            "09:00",
            "10:00",
            "meeting",
        ),
        make_event(
            "Break",
            "10:00",
            "10:30",
            "break",
        ),
        make_event(
            "Focused Work",
            "10:30",
            "11:30",
            "focused_work",
        ),
        make_event(
            "Lunch",
            "12:00",
            "13:00",
            "break",
        ),
        make_event(
            "Lecture",
            "13:30",
            "14:30",
            "lecture",
        ),
        make_event(
            "Break",
            "14:30",
            "15:00",
            "break",
        ),
        make_event(
            "Project Meeting",
            "15:00",
            "16:00",
            "meeting",
        ),
    ],
}


def run_scenarios():
    print()
    print("MINDSYNC HEURISTIC EVALUATION")
    print("=" * 75)

    for scenario_name, events in SCENARIOS.items():

        features = extract_calendar_features(events)

        result = calculate_stress_risk(features)

        density = result["heuristics"]["density"]["score"]
        recovery = result["heuristics"]["recovery"]["score"]
        context = result["heuristics"]["context"]["score"]

        print()
        print(scenario_name.upper())
        print("-" * 75)

        print(
            f"Density: {density}/100 | "
            f"Recovery: {recovery}/100 | "
            f"Context: {context}/100"
        )

        print(
            f"Combined: "
            f"{result['combined_score']}/100 "
            f"({result['risk_level']})"
        )


if __name__ == "__main__":
    run_scenarios()