from datetime import datetime


RECOVERY_TYPES = {"break", "lunch", "wellbeing"}

WORKLOAD_TYPES = {
    "meeting",
    "focused_work",
    "lecture",
    "presentation",
    "interview",
}


def calculate_gap_minutes(current_event, next_event):
    """
    calculate the free time in minutes between two consecutive events

    a value of:
    -> 0 means the events are directly back to back
    ->a positive value represents available free time
    -> a negative value represents overlapping events
    """

    gap = next_event["start_time"] - current_event["end_time"]

    return int(
        gap.total_seconds() / 60
    )


def is_recovery_event(event):
    """
    return True when an event represents an intentional recovery period
    """

    return event["type"] in RECOVERY_TYPES


def is_workload_event(event):
    """
    return True when an event represents cognitive or work related activity
    """

    return event["type"] in WORKLOAD_TYPES


def extract_calendar_features(
    events,
    workday_start="09:00",
    workday_end="17:00"
):
    """
    extract workload, recovery and context switching features
    from calendar events

    the resulting features are used by MindSync's
    interpretable rule-based stress risk heuristics 
    """

    day_start = datetime.strptime(
        workday_start,
        "%H:%M"
    )

    day_end = datetime.strptime(
        workday_end,
        "%H:%M"
    )

    workday_minutes = int(
        (day_end - day_start).total_seconds() / 60
    )

    if not events:
        return {
            "event_count": 0,
            "workload_event_count": 0,
            "meeting_count": 0,
            "recovery_event_count": 0,
            "total_workload_minutes": 0,
            "total_meeting_minutes": 0,
            "total_recovery_minutes": 0,
            "workday_minutes": workday_minutes,
            "workload_density": 0,
            "meeting_density": 0,
            "back_to_back_workload_count": 0,
            "short_gap_count": 0,
            "average_free_gap_minutes": 0,
            "minimum_free_gap_minutes": 0,
            "context_switches": 0,
            "unique_workload_types": 0,
        }

    workload_events = [
        event
        for event in events
        if is_workload_event(event)
    ]

    recovery_events = [
        event
        for event in events
        if is_recovery_event(event)
    ]

    meeting_events = [
        event
        for event in workload_events
        if event["type"] == "meeting"
    ]

    total_workload_minutes = sum(
        event["duration_minutes"]
        for event in workload_events
    )

    total_meeting_minutes = sum(
        event["duration_minutes"]
        for event in meeting_events
    )

    total_recovery_minutes = sum(
        event["duration_minutes"]
        for event in recovery_events
    )

    workload_density = (
        total_workload_minutes / workday_minutes
        if workday_minutes > 0
        else 0
    )

    meeting_density = (
        total_meeting_minutes / workday_minutes
        if workday_minutes > 0
        else 0
    )

    free_gaps = []

    back_to_back_workload_count = 0
    short_gap_count = 0
    context_switches = 0

    for index in range(len(events) - 1):

        current_event = events[index]
        next_event = events[index + 1]

        gap_minutes = calculate_gap_minutes(
            current_event,
            next_event
        )

        # only actual unallocated calendar time is considered a free gap
        if gap_minutes > 0:
            free_gaps.append(gap_minutes)

            if gap_minutes < 15:
                short_gap_count += 1

        # back to back pressure is only counted when both
        # events are workload activities 
        if (
            is_workload_event(current_event)
            and is_workload_event(next_event)
            and gap_minutes <= 0
        ):
            back_to_back_workload_count += 1

        # context switching is only measured between workload events
        # recovery events are deliberately excluded
        if (
            is_workload_event(current_event)
            and is_workload_event(next_event)
            and current_event["type"] != next_event["type"]
        ):
            context_switches += 1

    average_free_gap_minutes = (
        sum(free_gaps) / len(free_gaps)
        if free_gaps
        else 0
    )

    minimum_free_gap_minutes = (
        min(free_gaps)
        if free_gaps
        else 0
    )

    unique_workload_types = len(
        {
            event["type"]
            for event in workload_events
        }
    )

    return {
        "event_count": len(events),
        "workload_event_count": len(workload_events),
        "meeting_count": len(meeting_events),
        "recovery_event_count": len(recovery_events),

        "total_workload_minutes":
            total_workload_minutes,

        "total_meeting_minutes":
            total_meeting_minutes,

        "total_recovery_minutes":
            total_recovery_minutes,

        "workday_minutes":
            workday_minutes,

        "workload_density":
            round(workload_density, 3),

        "meeting_density":
            round(meeting_density, 3),

        "back_to_back_workload_count":
            back_to_back_workload_count,

        "short_gap_count":
            short_gap_count,

        "average_free_gap_minutes":
            round(average_free_gap_minutes, 1),

        "minimum_free_gap_minutes":
            minimum_free_gap_minutes,

        "context_switches":
            context_switches,

        "unique_workload_types":
            unique_workload_types,
    }