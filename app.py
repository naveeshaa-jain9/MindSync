from src.data_loader import load_calendar_from_json
from src.features import extract_calendar_features
from src.stress_engine import calculate_stress_risk
from src.recommendations import (
    generate_recommendations,
    prioritise_recommendations,
)
from src.scheduler import recommend_multiple_slots



def main():
    calendar = load_calendar_from_json(
        "data/sample_calendar.json"
    )

    print("MindSync")
    print("=" * 50)
    print(f"Calendar date: {calendar['date']}")
    print()

    # ----------------calendar events----------------

    print("CALENDAR EVENTS")
    print("-" * 50)

    for event in calendar["events"]:
        print(
            f"{event['start']} - {event['end']} | "
            f"{event['title']} | "
            f"{event['type']} | "
            f"{event['duration_minutes']} mins"
        )

    # -------------feature extraction---------------

    features = extract_calendar_features(
        calendar["events"]
    )

    print()
    print("EXTRACTED FEATURES")
    print("-" * 50)

    for feature_name, value in features.items():
        print(f"{feature_name}: {value}")

    # ------------stress risk analysis----------------

    risk = calculate_stress_risk(features)

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

        for reason in risk["adjustment_reasons"]:
            print(f"  - {reason}")

    print()

    for heuristic in risk["heuristics"].values():
        print(
            f"{heuristic['name']}: "
            f"{heuristic['score']}/100"
        )

        for reason in heuristic["reasons"]:
            print(f"  - {reason}")

        print()

    # --------------recommendations---------------

    candidate_recommendations = generate_recommendations(
        features,
        risk
    )

    recommendations = prioritise_recommendations(
        candidate_recommendations
    )

    scheduled_recommendations = recommend_multiple_slots(
        calendar["events"],
        recommendations
    )

    print("MINDSYNC RECOMMENDATIONS")
    print("-" * 50)

    for index, item in enumerate(
        scheduled_recommendations,
        start=1
    ):
        recommendation = item["recommendation"]
        slot = item["slot"]

        if index == 1:
            print("PRIMARY RECOMMENDATION")
        else:
            print("SECONDARY RECOMMENDATION")

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
                f"{slot['start']} - {slot['end']}"
            )

            print(
                f"Slot suitability: "
                f"{slot['suitability_score']}"
            )

            for reason in slot["reasons"]:
                print(f"  - {reason}")

        else:
            print(
                "Suggested time: "
                "No suitable free slot available."
            )

        print()

if __name__ == "__main__":
    main()