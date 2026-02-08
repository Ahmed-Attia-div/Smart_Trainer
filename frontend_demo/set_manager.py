"""
Handles set counting, rep quality, and set-level evaluation
"""

set_states = {}


def init_set_state(exercise_name, target_reps=10):
    """
    Initialize set tracking for an exercise
    """
    if exercise_name in set_states:
        return

    set_states[exercise_name] = {
        "current_reps": 0,
        "good_reps": 0,
        "bad_reps": 0,
        "sets": 0,
        "target_reps": target_reps,
        "last_rep_good": False,
        "set_finished": False,
        "last_set_quality": None
    }


def update_set(
    exercise_name,
    rep_detected: bool,
    rep_is_good: bool
):
    """
    Update set state when a rep is detected

    Args:
        rep_detected: True only when a NEW rep happens
        rep_is_good: True if rep form is correct

    Returns:
        dict with current state + events
    """

    init_set_state(exercise_name)
    state = set_states[exercise_name]

    event = {
        "rep_completed": False,
        "rep_good": False,
        "set_completed": False,
        "set_quality": None
    }

    if not rep_detected:
        return state, event

    state["current_reps"] += 1
    event["rep_completed"] = True

    if rep_is_good:
        state["good_reps"] += 1
        state["last_rep_good"] = True
        event["rep_good"] = True
    else:
        state["bad_reps"] += 1
        state["last_rep_good"] = False

    if state["current_reps"] >= state["target_reps"]:
        state["sets"] += 1
        state["set_finished"] = True

        quality_ratio = state["good_reps"] / state["target_reps"]

        if quality_ratio >= 0.85:
            state["last_set_quality"] = "excellent"
        elif quality_ratio >= 0.6:
            state["last_set_quality"] = "good"
        else:
            state["last_set_quality"] = "bad"

        event["set_completed"] = True
        event["set_quality"] = state["last_set_quality"]

        state["current_reps"] = 0
        state["good_reps"] = 0
        state["bad_reps"] = 0

    return state, event


def get_set_summary(exercise_name):
    """
    Returns a readable summary for UI
    """
    if exercise_name not in set_states:
        return ""

    s = set_states[exercise_name]
    return f"Sets: {s['sets']} | Reps: {s['current_reps']}/{s['target_reps']}"


def reset_sets(exercise_name):
    """
    Reset everything for an exercise
    """
    if exercise_name in set_states:
        del set_states[exercise_name]

# Alias for reset_sets
reset_set_state = reset_sets

def reset_all_sets():
    """Reset all set states - call this when starting a new session."""
    set_states.clear()  # استخدم clear() بدل = {} عشان الـ imports تشتغل صح
