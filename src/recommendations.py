def generate_recommendations(features, risk):
    """
    generate recovery recommendations from calendar features
    and stress risk analysis 

    recommendations are selected using interpretable rules so that
    each suggestion can be traced back to detected schedule pressure
    """

    recommendations = []

    density_score = risk["heuristics"]["density"]["score"]
    recovery_score = risk["heuristics"]["recovery"]["score"]
    context_score = risk["heuristics"]["context"]["score"]

    # ---------recovery pressure-------------

    if recovery_score >= 60:
        recommendations.append(
            {
                "activity": "Decompression Break",
                "duration_minutes": 15,
                "priority": "High",
                "reason": (
                    "Repeated back-to-back workload suggests "
                    "limited opportunities for cognitive recovery."
                ),
            }
        )

    elif recovery_score >= 30:
        recommendations.append(
            {
                "activity": "Short Recovery Break",
                "duration_minutes": 10,
                "priority": "Medium",
                "reason": (
                    "The schedule contains some consecutive workload "
                    "and would benefit from an additional recovery period."
                ),
            }
        )

    # ---------context switching-------------

    if context_score >= 70:
        recommendations.append(
            {
                "activity": "Focus Reset",
                "duration_minutes": 10,
                "priority": "High",
                "reason": (
                    "Frequent changes between workload categories "
                    "may increase cognitive switching demand."
                ),
            }
        )

    elif context_score >= 45:
        recommendations.append(
            {
                "activity": "Transition Pause",
                "duration_minutes": 5,
                "priority": "Medium",
                "reason": (
                    "Several workload context changes occur across "
                    "the analysed schedule."
                ),
            }
        )

    # ------workload density------------

    if density_score >= 75:
        recommendations.append(
            {
                "activity": "Extended Recovery Break",
                "duration_minutes": 20,
                "priority": "High",
                "reason": (
                    "A large proportion of the workday is occupied "
                    "by cognitively demanding activity."
                ),
            }
        )

    elif density_score >= 50:
        recommendations.append(
            {
                "activity": "Movement Break",
                "duration_minutes": 10,
                "priority": "Medium",
                "reason": (
                    "The calendar contains a moderately dense "
                    "workload distribution."
                ),
            }
        )

    # -------low pressure fallback--------------

    if not recommendations:
        recommendations.append(
            {
                "activity": "Preventative Micro-Break",
                "duration_minutes": 5,
                "priority": "Low",
                "reason": (
                    "Current calendar pressure is relatively low; "
                    "a brief preventative break can help maintain focus."
                ),
            }
        )

    return recommendations


def prioritise_recommendations(recommendations):
    """
    rank candidate wellbeing recommendations and return
    the strongest userfacing interventions
    recommendations are ranked by priority and then
    by duration so that higher impact activities are preferred
    when calendar pressure is substantial
    """

    priority_rank = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    ranked = sorted(
        recommendations,
        key=lambda recommendation: (
            priority_rank.get(
                recommendation["priority"],
                0
            ),
            recommendation["duration_minutes"],
        ),
        reverse=True,
    )

    # show at most two interventions to avoid overwhelming
    # the user with several overlapping recommendations
    return ranked[:2]