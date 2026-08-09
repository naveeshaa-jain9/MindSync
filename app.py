from datetime import date, datetime
from src.data_loader import load_calendar_from_json
from src.calendar_api import (
    load_google_calendar,
    get_events_for_date,
)
from src.features import extract_calendar_features
from src.stress_engine import calculate_stress_risk
from src.recommendations import (
    generate_recommendations,
    prioritise_recommendations,
)
from src.scheduler import recommend_multiple_slots


def load_calendar_data():
    """
    try to load live google calendar events first!!
    if Google Calendar is unavailable, authentication fails
    or no usable timed events are found for today, MindSync falls
    back to the bundled JSON sample calendar.
    """

    today = date.today().isoformat()

    try:
        google_events = load_google_calendar(
            days_ahead=7
        )

        todays_events = get_events_for_date(
            google_events,
            today
        )

        if todays_events:
            return {
                "date": today,
                "events": todays_events,
                "source": "LIVE GOOGLE CALENDAR",
                "fallback_reason": None,
            }

        fallback = load_calendar_from_json(
            "data/sample_calendar.json"
        )

        return {
            "date": fallback["date"],
            "events": fallback["events"],
            "source": "JSON FALLBACK",
            "fallback_reason": (
                "No usable timed Google Calendar events "
                "were found for today."
            ),
        }

    except Exception as error:
        fallback = load_calendar_from_json(
            "data/sample_calendar.json"
        )

        return {
            "date": fallback["date"],
            "events": fallback["events"],
            "source": "JSON FALLBACK",
            "fallback_reason": str(error),
        }


def main():
    calendar = load_calendar_data()

    print("MindSync")
    print("=" * 50)

    print(
        f"Data source: "
        f"{calendar['source']}"
    )

    if calendar["fallback_reason"]:
        print(
            f"Fallback reason: "
            f"{calendar['fallback_reason']}"
        )

    print(
        f"Calendar date: "
        f"{calendar['date']}"
    )

    print()

    # --------calendar events-----------

    print("CALENDAR EVENTS")
    print("-" * 50)

    for event in calendar["events"]:
        print(
            f"{event['start']} - {event['end']} | "
            f"{event['title']} | "
            f"{event['type']} | "
            f"{event['duration_minutes']} mins"
        )

    # -----------feature extraction------------

    features = extract_calendar_features(
        calendar["events"]
    )

    print()
    print("EXTRACTED FEATURES")
    print("-" * 50)

    for feature_name, value in features.items():
        print(
            f"{feature_name}: "
            f"{value}"
        )

    # -----------stress risk analysis------------

    risk = calculate_stress_risk(
        features
    )

    print()
    print("MINDSYNC STRESS-RISK ANALYSIS")
    print("-" * 50)

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
            f"Compound pressure adjustment: "
            f"+{risk['compound_adjustment']}"
        )

        for reason in risk[
            "adjustment_reasons"
        ]:
            print(
                f"  - {reason}"
            )

    print()

    for heuristic in risk[
        "heuristics"
    ].values():
        print(
            f"{heuristic['name']}: "
            f"{heuristic['score']}/100"
        )

        for reason in heuristic[
            "reasons"
        ]:
            print(
                f"  - {reason}"
            )

        print()

    # ---------recommendations-----------

    candidate_recommendations = (
        generate_recommendations(
            features,
            risk
        )
    )

    recommendations = (
        prioritise_recommendations(
            candidate_recommendations
        )
    )

    earliest_start = None

    if (
        calendar["source"] == "LIVE GOOGLE CALENDAR"
        and calendar["date"] == date.today().isoformat()
    ):
        earliest_start = datetime.now().strftime(
            "%H:%M"
        )

    scheduled_recommendations = (
        recommend_multiple_slots(
            calendar["events"],
            recommendations,
            earliest_start=earliest_start
        )
    )

    print(
        "MINDSYNC RECOMMENDATIONS"
    )

    print(
        "-" * 50
    )

    for index, item in enumerate(
        scheduled_recommendations,
        start=1
    ):
        recommendation = (
            item["recommendation"]
        )

        slot = item["slot"]

        if index == 1:
            print(
                "PRIMARY RECOMMENDATION"
            )
        else:
            print(
                "SECONDARY RECOMMENDATION"
            )

        print()

        print(
            f"{recommendation['activity']} "
            f"({recommendation['duration_minutes']} mins)"
        )

        print(
            f"Priority: "
            f"{recommendation['priority']}"
        )

        print(
            f"Reason: "
            f"{recommendation['reason']}"
        )

        if slot:
            print(
                f"Suggested time: "
                f"{slot['start']} - "
                f"{slot['end']}"
            )

            print(
                f"Slot suitability: "
                f"{slot['suitability_score']}"
            )

            for reason in slot[
                "reasons"
            ]:
                print(
                    f"  - {reason}"
                )

        else:
            print(
                "Suggested time: "
                "No suitable free slot available."
            )

        print()


if __name__ == "__main__":
    main()