def clamp_score(score):
    """
    keep a heuristic score within the 0to100 range
    """
    return max(0, min(100, round(score)))


def density_heuristic(features):
    """
    heuristic 1: workload density pressure

    estimates pressure from the proportion of the workday occupied
    by workload activities and meetings

    the thresholds are prototype design choices intended to
    operationalise calendar workload into an interpretable score
    """
    if features["workload_event_count"] == 0:
        return {
            "name": "Workload Density",
            "score": 0,
            "reasons": [
                "No workload events are scheduled in the analysed workday."
            ],
        }
    
    workload_density = features["workload_density"]
    meeting_density = features["meeting_density"]

    reasons = []

    # workload density contributes up to 70 points
    if workload_density < 0.40:
        workload_score = 15
    elif workload_density < 0.60:
        workload_score = 35
        reasons.append("More than 40% of the workday contains scheduled workload.")
    elif workload_density < 0.75:
        workload_score = 55
        reasons.append("More than 60% of the workday contains scheduled workload.")
    elif workload_density < 0.90:
        workload_score = 70
        reasons.append("More than 75% of the workday contains scheduled workload.")
    else:
        workload_score = 85
        reasons.append("More than 90% of the workday contains scheduled workload.")

    # meeting concentration contributes additional pressure
    if meeting_density >= 0.60:
        meeting_adjustment = 15
        reasons.append("Meetings occupy at least 60% of the analysed workday.")
    elif meeting_density >= 0.40:
        meeting_adjustment = 10
        reasons.append("Meetings occupy at least 40% of the analysed workday.")
    elif meeting_density >= 0.25:
        meeting_adjustment = 5
    else:
        meeting_adjustment = 0

    score = clamp_score(
        workload_score + meeting_adjustment
    )

    if not reasons:
        reasons.append("The schedule has relatively low workload density.")

    return {
        "name": "Workload Density",
        "score": score,
        "reasons": reasons,
    }


def recovery_heuristic(features):
    """
    heuristic 2: recovery pressure.

    estimates pressure caused by consecutive workload events,
    short opportunities for recovery and limited explicit breaks
    """
    if features["workload_event_count"] == 0:
        return {
            "name": "Recovery Pressure",
            "score": 0,
            "reasons": [
                "No workload is scheduled, so no additional recovery pressure is detected."
            ],
        }
    
    score = 0
    reasons = []

    back_to_back = features["back_to_back_workload_count"]
    short_gaps = features["short_gap_count"]
    recovery_minutes = features["total_recovery_minutes"]
    minimum_gap = features["minimum_free_gap_minutes"]

    # consecutive workload events
    score += min(back_to_back * 15, 45)

    if back_to_back >= 3:
        reasons.append(
            f"{back_to_back} back-to-back workload transitions reduce recovery opportunities."
        )
    elif back_to_back > 0:
        reasons.append(
            f"{back_to_back} back-to-back workload transition(s) detected."
        )

    # very short free gaps
    score += min(short_gaps * 10, 30)

    if short_gaps > 0:
        reasons.append(
            f"{short_gaps} free gap(s) are shorter than 15 minutes."
        )

    # limited deliberately scheduled recovery
    if recovery_minutes == 0:
        score += 20
        reasons.append(
            "No explicit recovery or break event is scheduled."
        )
    elif recovery_minutes < 30:
        score += 10
        reasons.append(
            "Less than 30 minutes of explicit recovery time is scheduled."
        )
    else:
        reasons.append(
            f"{recovery_minutes} minutes of explicit recovery time are scheduled."
        )

    # minimum free gap signal
    if minimum_gap == 0:
        score += 10
    elif minimum_gap < 15:
        score += 10
    elif minimum_gap >= 30:
        score -= 5

    score = clamp_score(score)

    if not reasons:
        reasons.append(
            "The schedule contains reasonable opportunities for recovery."
        )

    return {
        "name": "Recovery Pressure",
        "score": score,
        "reasons": reasons,
    }


def context_switching_heuristic(features):
    """
    heuristic 3: context switching pressure

    estimates cognitive switching demand from changes between
    workload categories and the diversity of scheduled workload

    small schedules are treated conservatively because a single
    transition should not automatically imply severe switching pressure
    """

    switches = features["context_switches"]
    unique_types = features["unique_workload_types"]
    workload_events = features["workload_event_count"]

    reasons = []

    if workload_events <= 1:
        return {
            "name": "Context Switching",
            "score": 0,
            "reasons": [
                "Too few workload events are present to create meaningful switching pressure."
            ],
        }

    # a very small schedule should not receive an extreme score
    # simply because its two activities are different
    if workload_events == 2:
        score = switches * 15

        if unique_types > 1:
            score += 5

        if switches > 0:
            reasons.append(
                "A single workload context transition occurs, but the overall schedule is light."
            )
        else:
            reasons.append(
                "No workload context switching was detected."
            )

        return {
            "name": "Context Switching",
            "score": clamp_score(score),
            "reasons": reasons,
        }

    possible_switches = workload_events - 1

    switch_ratio = min(
        switches / possible_switches,
        1
    )

    #switching frequency contributes up to 60 points
    score = switch_ratio * 60

    # diversity contributes up to another 24 points
    diversity_adjustment = min(
        max(unique_types - 1, 0) * 8,
        24
    )

    score += diversity_adjustment

    if switches >= 4:
        reasons.append(
            f"{switches} workload context switches occur across the day."
        )
    elif switches > 0:
        reasons.append(
            f"{switches} workload context switch(es) occur across the day."
        )
    else:
        reasons.append(
            "No workload context switches were detected."
        )

    if unique_types >= 3:
        reasons.append(
            f"The schedule contains {unique_types} different workload categories."
        )

    return {
        "name": "Context Switching",
        "score": clamp_score(score),
        "reasons": reasons,
    }


def classify_risk(score):
    """
    convert a numerical score into an interpretable risk category
    """

    if score < 35:
        return "Low"

    if score < 65:
        return "Moderate"

    return "High"


def calculate_stress_risk(features):
    """
    run all three heuristic strategies and combine their outputs

    the combined score is an interpretable calendar based workload
    pressure estimate rather than a clinical measurement of stress

    a compound pressure adjustment is applied when multiple
    complementary indicators simultaneously show substantial pressure
    """

    density = density_heuristic(features)
    recovery = recovery_heuristic(features)
    context = context_switching_heuristic(features)

    weights = {
        "density": 0.35,
        "recovery": 0.35,
        "context": 0.30,
    }

    base_score = (
        density["score"] * weights["density"]
        + recovery["score"] * weights["recovery"]
        + context["score"] * weights["context"]
    )

    adjustment = 0
    adjustment_reasons = []

    # severe recovery pressure combined with a dense schedule
    # should not be diluted by a low context-switching score
    if (
        recovery["score"] >= 70
        and density["score"] >= 60
    ):
        adjustment += 15

        adjustment_reasons.append(
            "High recovery pressure occurs alongside substantial workload density."
        )

    # a very dense day with several back-to-back workload
    # transitions receives a smaller compound-pressure increase
    elif (
        density["score"] >= 75
        and features["back_to_back_workload_count"] >= 3
    ):
        adjustment += 5

        adjustment_reasons.append(
            "High workload density is combined with repeated back-to-back activities."
        )

    combined_score = clamp_score(
        base_score + adjustment
    )

    return {
        "base_score": clamp_score(base_score),
        "combined_score": combined_score,
        "risk_level": classify_risk(combined_score),

        "heuristics": {
            "density": density,
            "recovery": recovery,
            "context": context,
        },

        "weights": weights,
        "compound_adjustment": adjustment,
        "adjustment_reasons": adjustment_reasons,
    }