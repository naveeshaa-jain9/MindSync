from datetime import datetime


def time_to_minutes(time_string):
    """
    convert a HH:MM time string into minutes after midnight
    """

    time_value = datetime.strptime(time_string, "%H:%M")

    return (
        time_value.hour * 60
        + time_value.minute
    )


def minutes_to_time(total_minutes):
    """
    convert minutes after midnight back into HH:MM format
    """

    hours = total_minutes // 60
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"


def find_free_slots(
    events,
    workday_start="09:00",
    workday_end="17:00",
    earliest_start=None
):
    """
    find unallocated periods between calendar events

    if earliest_start is provided, free slots before that time
    are ignored. This is useful for live calendar analysis so
    MindSync does not recommend breaks in the past
    """

    start_minutes = time_to_minutes(
        workday_start
    )

    if earliest_start is not None:
        start_minutes = max(
            start_minutes,
            time_to_minutes(
                earliest_start
            )
        )

    end_minutes = time_to_minutes(
        workday_end
    )

    free_slots = []

    if start_minutes >= end_minutes:
        return free_slots

    if not events:
        return [
            {
                "start": minutes_to_time(
                    start_minutes
                ),
                "end": workday_end,
                "duration_minutes": (
                    end_minutes
                    - start_minutes
                ),
            }
        ]

    current_time = start_minutes

    for event in events:
        event_start = time_to_minutes(
            event["start"]
        )

        event_end = time_to_minutes(
            event["end"]
        )

        #ignore events that finish before
        # the current analysis window
        if event_end <= start_minutes:
            continue

        #stop once events begin after
        # the configured workday
        if event_start >= end_minutes:
            break

        event_start = max(
            event_start,
            start_minutes
        )

        event_end = min(
            event_end,
            end_minutes
        )

        if event_start > current_time:
            free_slots.append(
                {
                    "start": minutes_to_time(
                        current_time
                    ),
                    "end": minutes_to_time(
                        event_start
                    ),
                    "duration_minutes": (
                        event_start
                        - current_time
                    ),
                }
            )

        current_time = max(
            current_time,
            event_end
        )

    if current_time < end_minutes:
        free_slots.append(
            {
                "start": minutes_to_time(
                    current_time
                ),
                "end": minutes_to_time(
                    end_minutes
                ),
                "duration_minutes": (
                    end_minutes
                    - current_time
                ),
            }
        )

    return free_slots


def score_slot(
    slot,
    recommendation,
    events
):
    """
    score a free slot for a recommendation

    higher scores indicate more suitable
    recovery opportunities
    """

    required_duration = (
        recommendation[
            "duration_minutes"
        ]
    )

    if (
        slot["duration_minutes"]
        < required_duration
    ):
        return None

    score = 0
    reasons = []

    extra_space = (
        slot["duration_minutes"]
        - required_duration
    )

    if extra_space >= 15:
        score += 15

        reasons.append(
            "The slot comfortably fits "
            "the recommended activity."
        )

    else:
        score += 10

        reasons.append(
            "The slot fits "
            "the recommended activity."
        )

    slot_start = time_to_minutes(
        slot["start"]
    )

    if (
        slot_start
        >= time_to_minutes("11:00")
    ):
        score += 5

    preceding_event = None

    for event in events:
        if (
            event["end"]
            == slot["start"]
        ):
            preceding_event = event
            break

    if (
        preceding_event
        and preceding_event["type"]
        != "break"
        and preceding_event["type"]
        != "wellbeing"
    ):
        score += 10

        reasons.append(
            "The slot follows "
            "scheduled workload."
        )

    return {
        "score": score,
        "reasons": reasons,
    }


def get_candidate_slots(
    events,
    recommendation,
    workday_start="09:00",
    workday_end="17:00",
    earliest_start=None
):
    """
    return all suitable candidate slots
    for a recommendation
    """

    free_slots = find_free_slots(
        events,
        workday_start,
        workday_end,
        earliest_start
    )

    candidates = []

    for slot in free_slots:
        evaluation = score_slot(
            slot,
            recommendation,
            events
        )

        if evaluation is None:
            continue

        proposed_start = time_to_minutes(
            slot["start"]
        )

        proposed_end = (
            proposed_start
            + recommendation[
                "duration_minutes"
            ]
        )

        candidates.append(
            {
                "start":
                    slot["start"],

                "end":
                    minutes_to_time(
                        proposed_end
                    ),

                "available_window_start":
                    slot["start"],

                "available_window_end":
                    slot["end"],

                "activity":
                    recommendation[
                        "activity"
                    ],

                "duration_minutes":
                    recommendation[
                        "duration_minutes"
                    ],

                "suitability_score":
                    evaluation[
                        "score"
                    ],

                "reasons":
                    evaluation[
                        "reasons"
                    ],
            }
        )

    candidates.sort(
        key=lambda candidate: (
            -candidate[
                "suitability_score"
            ],
            time_to_minutes(
                candidate["start"]
            ),
        )
    )

    return candidates


def recommend_slot(
    events,
    recommendation,
    workday_start="09:00",
    workday_end="17:00",
    earliest_start=None
):
    """
    select the highest-scoring free slot
    for one recommendation
    """

    candidates = get_candidate_slots(
        events,
        recommendation,
        workday_start,
        workday_end,
        earliest_start
    )

    if not candidates:
        return None

    return candidates[0]


def recommend_multiple_slots(
    events,
    recommendations,
    workday_start="09:00",
    workday_end="17:00",
    earliest_start=None
):
    """
    assign non-overlapping slots to multiple recommendations

    where possible, later recommendations are placed in a
    different free window from earlier recommendations

    if earliest_start is provided, no recommendation will be
    scheduled before that time
    """

    scheduled = []

    temporary_events = list(
        events
    )

    used_windows = set()

    for recommendation in recommendations:
        candidates = get_candidate_slots(
            temporary_events,
            recommendation,
            workday_start,
            workday_end,
            earliest_start
        )

        if not candidates:
            scheduled.append(
                {
                    "recommendation":
                        recommendation,

                    "slot":
                        None,
                }
            )

            continue

        chosen_slot = None

        for candidate in candidates:
            window_key = (
                candidate[
                    "available_window_start"
                ],
                candidate[
                    "available_window_end"
                ],
            )

            if (
                window_key
                not in used_windows
            ):
                chosen_slot = candidate

                used_windows.add(
                    window_key
                )

                break

        if chosen_slot is None:
            chosen_slot = (
                candidates[0]
            )

        scheduled.append(
            {
                "recommendation":
                    recommendation,

                "slot":
                    chosen_slot,
            }
        )

        temporary_events.append(
            {
                "title":
                    recommendation[
                        "activity"
                    ],

                "start":
                    chosen_slot[
                        "start"
                    ],

                "end":
                    chosen_slot[
                        "end"
                    ],

                "type":
                    "wellbeing",
            }
        )

        temporary_events.sort(
            key=lambda event:
                time_to_minutes(
                    event["start"]
                )
        )

    return scheduled