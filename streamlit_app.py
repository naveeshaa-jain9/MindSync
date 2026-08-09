from datetime import date, datetime
from textwrap import dedent

import streamlit as st

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


st.set_page_config(
    page_title="MindSync",
    page_icon="🧠",
    layout="wide",
)


CUSTOM_CSS = """
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

.hero {
    padding: 1.8rem 2rem;
    border: 1px solid rgba(120, 120, 120, 0.25);
    border-radius: 18px;
    margin-bottom: 1.5rem;
    background: rgba(120, 120, 120, 0.05);
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    opacity: 0.75;
}

.section-heading {
    font-size: 1.45rem;
    font-weight: 700;
    margin-top: 0.5rem;
    margin-bottom: 0.8rem;
}

.metric-card {
    border: 1px solid rgba(120, 120, 120, 0.24);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    background: rgba(120, 120, 120, 0.04);
    height: 100%;
}

.metric-label {
    font-size: 0.85rem;
    opacity: 0.7;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 750;
}

.risk-card {
    border: 1px solid rgba(120, 120, 120, 0.24);
    border-radius: 18px;
    padding: 1.6rem;
    background: rgba(120, 120, 120, 0.04);
    height: 100%;
}

.risk-number {
    font-size: 3.2rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.risk-level {
    font-size: 1.45rem;
    font-weight: 750;
    margin-bottom: 0.6rem;
}

.recommendation-card {
    border: 1px solid rgba(120, 120, 120, 0.24);
    border-radius: 18px;
    padding: 1.3rem 1.4rem;
    margin-bottom: 1rem;
    background: rgba(120, 120, 120, 0.035);
}

.primary-card {
    border-left: 6px solid #ff4b4b;
}

.secondary-card {
    border-left: 6px solid #ffa421;
}

.rec-title {
    font-size: 1.35rem;
    font-weight: 750;
    margin-bottom: 0.25rem;
}

.rec-label {
    font-size: 0.8rem;
    opacity: 0.65;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.time-pill {
    display: inline-block;
    border-radius: 999px;
    padding: 0.45rem 0.8rem;
    margin-top: 0.7rem;
    background: rgba(46, 204, 113, 0.15);
    font-weight: 650;
}

.calendar-row {
    border: 1px solid rgba(120, 120, 120, 0.20);
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.65rem;
    background: rgba(120, 120, 120, 0.03);
}

.calendar-time {
    font-size: 1rem;
    font-weight: 750;
}

.calendar-title {
    font-size: 1rem;
    font-weight: 650;
}

.calendar-type {
    font-size: 0.82rem;
    opacity: 0.65;
}

.small-muted {
    font-size: 0.82rem;
    opacity: 0.65;
}

</style>
"""


def load_calendar_data():
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
                "source": "Live Google Calendar",
                "fallback_reason": None,
            }

        fallback = load_calendar_from_json(
            "data/sample_calendar.json"
        )

        return {
            "date": fallback["date"],
            "events": fallback["events"],
            "source": "JSON Fallback",
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
            "source": "JSON Fallback",
            "fallback_reason": str(error),
        }


def risk_emoji(risk_level):
    if risk_level == "High":
        return "🔴"

    if risk_level == "Moderate":
        return "🟠"

    return "🟢"


def format_minutes(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours == 0:
        return f"{remaining_minutes} min"

    if remaining_minutes == 0:
        return f"{hours} hr"

    return (
        f"{hours} hr "
        f"{remaining_minutes} min"
    )


def render_metric_card(label, value):
    html = dedent(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value">
                {value}
            </div>
        </div>
        """
    )

    st.html(html)


def render_calendar_event(event):
    event_type = (
        event["type"]
        .replace("_", " ")
        .title()
    )

    html = dedent(
        f"""
        <div class="calendar-row">
            <div style="
                display:grid;
                grid-template-columns:140px 1fr 100px;
                gap:1rem;
                align-items:center;
            ">
                <div class="calendar-time">
                    {event['start']} – {event['end']}
                </div>

                <div>
                    <div class="calendar-title">
                        {event['title']}
                    </div>

                    <div class="calendar-type">
                        {event_type}
                    </div>
                </div>

                <div style="
                    text-align:right;
                    font-weight:600;
                ">
                    {event['duration_minutes']} min
                </div>
            </div>
        </div>
        """
    )

    st.html(html)


def main():
    st.markdown(
        CUSTOM_CSS,
        unsafe_allow_html=True,
    )

    calendar = load_calendar_data()

    features = extract_calendar_features(
        calendar["events"]
    )

    risk = calculate_stress_risk(
        features
    )

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
        calendar["source"] == "Live Google Calendar"
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

    display_recommendations = [
        item
        for item in scheduled_recommendations
        if item.get("slot") is not None
    ]

    # -------sidebar---------

    with st.sidebar:
        st.markdown("## 🧠 MindSync")

        st.caption(
            "Calendar-based workload and wellbeing intelligence"
        )

        st.divider()

        st.markdown("### Data Source")

        if calendar["source"] == "Live Google Calendar":
            st.success(
                "Live Google Calendar"
            )
        else:
            st.warning(
                "JSON Fallback"
            )

        st.markdown("### Analysed Date")
        st.write(
            calendar["date"]
        )

        st.markdown("### Analysis Window")
        st.write(
            "09:00 – 17:00"
        )

        st.divider()

        st.markdown("### Model")

        st.write(
            "Rule-based AI"
        )

        st.caption(
            "Three interpretable heuristics:"
        )

        st.write("• Workload density")
        st.write("• Recovery pressure")
        st.write("• Context switching")

        st.divider()

        st.caption(
            "MindSync estimates calendar-based workload "
            "pressure and does not provide a clinical diagnosis."
        )

    # ---------hero------------

    hero_html = dedent(
        """
        <div class="hero">
            <div class="hero-title">
                🧠 MindSync
            </div>

            <div class="hero-subtitle">
                Your intelligent calendar-based wellbeing companion
            </div>
        </div>
        """
    )

    st.html(
        hero_html
    )

    source_col, date_col = st.columns(
        [2, 1]
    )

    with source_col:
        if calendar["source"] == "Live Google Calendar":
            st.success(
                "Connected to Live Google Calendar"
            )
        else:
            st.warning(
                "Using JSON fallback demonstration data"
            )

            if calendar["fallback_reason"]:
                st.caption(
                    calendar["fallback_reason"]
                )

    with date_col:
        st.markdown(
            f"**Analysed date:** {calendar['date']}"
        )

    # --------overview-------------

    st.markdown(
        '<div class="section-heading">'
        "Workload Overview"
        "</div>",
        unsafe_allow_html=True,
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    with metric_1:
        render_metric_card(
            "Workload Events",
            features[
                "workload_event_count"
            ],
        )

    with metric_2:
        render_metric_card(
            "Workload Time",
            format_minutes(
                features[
                    "total_workload_minutes"
                ]
            ),
        )

    with metric_3:
        render_metric_card(
            "Workload Density",
            (
                f"{features['workload_density'] * 100:.1f}%"
            ),
        )

    with metric_4:
        render_metric_card(
            "Back-to-Back",
            features[
                "back_to_back_workload_count"
            ],
        )

    st.write("")

    # -----------risk analysis------------

    st.markdown(
        '<div class="section-heading">'
        "Stress-Risk Analysis"
        "</div>",
        unsafe_allow_html=True,
    )

    risk_col, heuristics_col = (
        st.columns(
            [0.9, 2.1]
        )
    )

    with risk_col:
        risk_html = dedent(
            f"""
            <div class="risk-card">
                <div class="small-muted">
                    Combined Risk Score
                </div>

                <div class="risk-number">
                    {risk['combined_score']}/100
                </div>

                <div class="risk-level">
                    {risk_emoji(risk['risk_level'])}
                    {risk['risk_level'].upper()}
                </div>

                <div class="small-muted">
                    Interpretable calendar-based
                    workload-pressure estimate.
                </div>
            </div>
            """
        )

        st.html(
            risk_html
        )

    with heuristics_col:
        for heuristic in risk[
            "heuristics"
        ].values():
            score = heuristic[
                "score"
            ]

            st.markdown(
                f"**{heuristic['name']}** "
                f"— {score}/100"
            )

            st.progress(
                score / 100
            )

    # --------explainability-------------

    st.markdown(
        '<div class="section-heading">'
        "Why MindSync Produced This Result"
        "</div>",
        unsafe_allow_html=True,
    )

    if risk[
        "adjustment_reasons"
    ]:
        for reason in risk[
            "adjustment_reasons"
        ]:
            st.info(
                reason
            )

    explain_1, explain_2, explain_3 = (
        st.columns(3)
    )

    heuristic_values = list(
        risk[
            "heuristics"
        ].values()
    )

    explain_columns = [
        explain_1,
        explain_2,
        explain_3,
    ]

    for column, heuristic in zip(
        explain_columns,
        heuristic_values
    ):
        with column:
            with st.expander(
                heuristic[
                    "name"
                ]
            ):
                for reason in heuristic[
                    "reasons"
                ]:
                    st.write(
                        f"• {reason}"
                    )

    # ----------recommendations------------

    st.markdown(
        '<div class="section-heading">'
        "Personalised Recovery Recommendations"
        "</div>",
        unsafe_allow_html=True,
    )

    if display_recommendations:
        for index, item in enumerate(
            display_recommendations,
            start=1
        ):
            recommendation = (
                item[
                    "recommendation"
                ]
            )

            slot = item[
                "slot"
            ]

            if index == 1:
                card_class = (
                    "recommendation-card "
                    "primary-card"
                )

                label = (
                    "Primary Recommendation"
                )

            else:
                card_class = (
                    "recommendation-card "
                    "secondary-card"
                )

                label = (
                    "Secondary Recommendation"
                )

            slot_text = (
                f"{slot['start']} – "
                f"{slot['end']}"
            )

            recommendation_html = dedent(
                f"""
                <div class="{card_class}">
                    <div class="rec-label">
                        {label}
                    </div>

                    <div class="rec-title">
                        {recommendation['activity']}
                    </div>

                    <div style="
                        display:flex;
                        gap:2.5rem;
                        margin-top:0.7rem;
                        margin-bottom:0.7rem;
                    ">
                        <div>
                            <div class="small-muted">
                                Duration
                            </div>

                            <b>
                                {recommendation['duration_minutes']} min
                            </b>
                        </div>

                        <div>
                            <div class="small-muted">
                                Priority
                            </div>

                            <b>
                                {recommendation['priority']}
                            </b>
                        </div>
                    </div>

                    <div>
                        {recommendation['reason']}
                    </div>

                    <div class="time-pill">
                        Suggested time: {slot_text}
                    </div>
                </div>
                """
            )

            st.html(
                recommendation_html
            )

            with st.expander(
                "Why this time was selected"
            ):
                for reason in slot[
                    "reasons"
                ]:
                    st.write(
                        f"• {reason}"
                    )

    else:
        st.info(
            "No additional recovery intervention can be fitted "
            "into the remaining analysed workday."
        )

    # -------calendar-----------

    st.markdown(
        '<div class="section-heading">'
        "Calendar Timeline"
        "</div>",
        unsafe_allow_html=True,
    )

    if not calendar[
        "events"
    ]:
        st.info(
            "No calendar events were found."
        )

    else:
        for event in calendar[
            "events"
        ]:
            render_calendar_event(
                event
            )

    # ------------tech details-----------

    st.write("")

    with st.expander(
        "Technical Details"
    ):
        st.markdown(
            "#### Extracted Features"
        )

        st.json(
            features
        )

        st.markdown(
            "#### Model Weights"
        )

        st.json(
            risk[
                "weights"
            ]
        )

        st.markdown(
            "#### Compound Adjustment"
        )

        st.write(
            risk[
                "compound_adjustment"
            ]
        )


if __name__ == "__main__":
    main()