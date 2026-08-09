from datetime import datetime

from src.features import extract_calendar_features
from src.stress_engine import calculate_stress_risk


def event(
    title,
    start,
    end,
    event_type,
    duration
):
    """
    creeate a calendar event in the same structure
    expected by the MindSync feature extraction pipeline
    """

    start_time = datetime.strptime(
        start,
        "%H:%M"
    )

    end_time = datetime.strptime(
        end,
        "%H:%M"
    )

    return {
        "title": title,
        "start": start,
        "end": end,
        "type": event_type,
        "duration_minutes": duration,
        "start_time": start_time,
        "end_time": end_time,
    }


evaluation_cases = {
    "Light Day": [
        event(
            "Morning Meeting",
            "10:00",
            "10:30",
            "meeting",
            30
        ),
        event(
            "Focused Work",
            "14:00",
            "15:00",
            "focused_work",
            60
        ),
    ],

    "Moderate Day": [
        event(
            "Team Meeting",
            "09:00",
            "10:00",
            "meeting",
            60
        ),
        event(
            "Programming",
            "10:30",
            "12:00",
            "focused_work",
            90
        ),
        event(
            "Lunch",
            "12:00",
            "13:00",
            "break",
            60
        ),
        event(
            "Lecture",
            "14:00",
            "15:00",
            "lecture",
            60
        ),
    ],

    "High Density Day": [
        event(
            "Meeting 1",
            "09:00",
            "10:00",
            "meeting",
            60
        ),
        event(
            "Programming",
            "10:00",
            "12:00",
            "focused_work",
            120
        ),
        event(
            "Meeting 2",
            "12:00",
            "13:00",
            "meeting",
            60
        ),
        event(
            "Lecture",
            "13:00",
            "14:00",
            "lecture",
            60
        ),
        event(
            "Project Work",
            "14:00",
            "16:30",
            "focused_work",
            150
        ),
    ],

    "Back-to-Back Heavy": [
        event(
            "Meeting 1",
            "09:00",
            "10:00",
            "meeting",
            60
        ),
        event(
            "Meeting 2",
            "10:00",
            "11:00",
            "meeting",
            60
        ),
        event(
            "Meeting 3",
            "11:00",
            "12:00",
            "meeting",
            60
        ),
        event(
            "Programming",
            "12:00",
            "13:00",
            "focused_work",
            60
        ),
    ],

    "Context Switch Heavy": [
        event(
            "Meeting",
            "09:00",
            "09:45",
            "meeting",
            45
        ),
        event(
            "Programming",
            "10:00",
            "10:45",
            "focused_work",
            45
        ),
        event(
            "Lecture",
            "11:00",
            "11:45",
            "lecture",
            45
        ),
        event(
            "Meeting",
            "12:00",
            "12:45",
            "meeting",
            45
        ),
        event(
            "Programming",
            "13:00",
            "13:45",
            "focused_work",
            45
        ),
        event(
            "Lecture",
            "14:00",
            "14:45",
            "lecture",
            45
        ),
    ],

    "Recovery Rich Day": [
        event(
            "Programming",
            "09:00",
            "10:00",
            "focused_work",
            60
        ),
        event(
            "Break",
            "10:00",
            "10:30",
            "break",
            30
        ),
        event(
            "Meeting",
            "11:00",
            "12:00",
            "meeting",
            60
        ),
        event(
            "Lunch",
            "12:00",
            "13:00",
            "break",
            60
        ),
        event(
            "Project Work",
            "14:00",
            "15:00",
            "focused_work",
            60
        ),
    ],

    "Single Event Day": [
        event(
            "Project Meeting",
            "14:00",
            "15:00",
            "meeting",
            60
        ),
    ],

    "Empty Day": [],
}


def run_evaluation():
    print()
    print("=" * 75)
    print("MINDSYNC SYSTEM EVALUATION")
    print("=" * 75)

    for case_name, events in evaluation_cases.items():
        features = extract_calendar_features(
            events
        )

        risk = calculate_stress_risk(
            features
        )

        print()
        print(case_name.upper())
        print("-" * 75)

        print(
            f"Workload events: "
            f"{features['workload_event_count']}"
        )

        print(
            f"Workload density: "
            f"{features['workload_density']:.3f}"
        )

        print(
            f"Back-to-back: "
            f"{features['back_to_back_workload_count']}"
        )

        print(
            f"Context switches: "
            f"{features['context_switches']}"
        )

        print(
            f"Recovery minutes: "
            f"{features['total_recovery_minutes']}"
        )

        print()

        print(
            f"Density score: "
            f"{risk['heuristics']['density']['score']}/100"
        )

        print(
            f"Recovery score: "
            f"{risk['heuristics']['recovery']['score']}/100"
        )

        print(
            f"Context score: "
            f"{risk['heuristics']['context']['score']}/100"
        )

        print(
            f"Combined score: "
            f"{risk['combined_score']}/100"
        )

        print(
            f"Risk level: "
            f"{risk['risk_level'].upper()}"
        )

        if risk["compound_adjustment"] > 0:
            print(
                f"Compound adjustment: "
                f"+{risk['compound_adjustment']}"
            )


if __name__ == "__main__":
    run_evaluation()