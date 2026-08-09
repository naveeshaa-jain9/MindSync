from src.data_loader import load_calendar_from_json
from src.features import extract_calendar_features
from src.stress_engine import calculate_stress_risk

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

if __name__ == "__main__":
    main()