from exercises_angles import EXERCISE_RULES

rep_states = {}

# تمارين تحتاج عد مزدوج (يمين + شمال = عدة واحدة)
DOUBLE_REP_EXERCISES = ["russian twist"]

def reset_all_reps():
    """Reset all rep states - call this when starting a new session."""
    rep_states.clear()

def init_rep_state(exercise_name, tolerance=15):
    """
    Initialize tracking state for an exercise.
    tolerance: نسمح بفرق بسيط من الـ min/max للسماح بالتنوع في الحركة
    """
    rules = EXERCISE_RULES.get(exercise_name, {})
    if not rules:
        return

    # نبحث عن أول joint فيه min/max
    for joint, rule in rules.items():
        if "min" in rule and "max" in rule:
            min_val = rule["min"]
            max_val = rule["max"]
            
            # هل التمرين ده محتاج عد مزدوج؟
            is_double = exercise_name.lower() in DOUBLE_REP_EXERCISES
            
            # Use explicit rep thresholds if defined, otherwise derive from min/max with tolerance
            rep_start_val = rule.get("rep_start", min_val + tolerance)
            rep_end_val = rule.get("rep_end", max_val - tolerance)
            
            rep_states[exercise_name] = {
                "joint": joint,
                "min_val": rep_start_val,
                "max_val": rep_end_val,
                "start_reached": False,
                "end_reached": False,
                "count": 0,
                "cycles": 0,
                "is_double_rep": is_double,
                "cooldown": 0,
                "last_angle": None,
                # NEW: Track peak angles for ALL joints during current rep
                "peak_angles": {},  # Will store min values for each joint during rep
                "in_rep": False,    # Are we currently in a rep cycle?
                "last_rep_peaks": None,  # Peaks from the last completed rep (for feedback)
            }
            break


def update_reps(exercise_name, all_angles, delay_frames=3):
    """
    Update the rep count based on current angles.
    
    Args:
        exercise_name: Name of the exercise
        all_angles: Dictionary with ALL joint angles {"elbow": x, "shoulder": y, "knee": z, "hip": w}
        delay_frames: Cooldown between rep counts
    
    Returns:
        tuple: (current_count, rep_just_completed, peak_angles_of_completed_rep)
               - current_count: Total reps counted
               - rep_just_completed: True if a rep was just counted this frame
               - peak_angles_of_completed_rep: Dict of peak angles for the completed rep (or None)
    """
    if exercise_name not in rep_states:
        init_rep_state(exercise_name)
        if exercise_name not in rep_states:
            return 0, False, None

    state = rep_states[exercise_name]
    primary_joint = state["joint"]
    
    # Get primary angle for counting
    if primary_joint not in all_angles:
        return state["count"], False, None
    
    angle = all_angles[primary_joint]

    # Cooldown بين العدات
    if state["cooldown"] > 0:
        state["cooldown"] -= 1
        # Still track peaks during cooldown if in rep
        if state["in_rep"]:
            _update_peak_tracking(state, all_angles)
        return state["count"], False, None

    min_thresh = state["min_val"]
    max_thresh = state["max_val"]

    # DEBUG: Print current angle vs thresholds
    print(f"[{exercise_name}] angle={angle:.0f} | need <={min_thresh:.0f} for START, >={max_thresh:.0f} for END | start={state['start_reached']} end={state['end_reached']}")

    # Track if a rep was just completed
    rep_completed = False
    completed_peaks = None

    # نتتبع هل وصلنا للبداية (الزاوية الصغيرة)
    if angle <= min_thresh:
        state["start_reached"] = True
        state["in_rep"] = True  # We're now in a rep
        
    # Update peak tracking while in rep
    if state["in_rep"]:
        _update_peak_tracking(state, all_angles)
    
    # نتتبع هل وصلنا للنهاية (الزاوية الكبيرة) بعد البداية
    if angle >= max_thresh and state["start_reached"]:
        state["end_reached"] = True

    # لما نوصل للاتنين، نحسب دورة
    if state["start_reached"] and state["end_reached"]:
        state["cycles"] += 1
        state["start_reached"] = False
        state["end_reached"] = False
        state["cooldown"] = delay_frames
        
        # Save peak angles from this rep before resetting
        completed_peaks = state["peak_angles"].copy()
        state["last_rep_peaks"] = completed_peaks
        
        # Reset peak tracking for next rep
        state["peak_angles"] = {}
        state["in_rep"] = False
        
        # لو عد مزدوج (Russian Twist): كل دورتين = عدة واحدة
        if state["is_double_rep"]:
            if state["cycles"] % 2 == 0:
                state["count"] += 1
                rep_completed = True
                print(f"[REP] COUNTED (Double)! Total: {state['count']} (cycles: {state['cycles']})")
            else:
                print(f"[REP] Half rep... (cycles: {state['cycles']})")
                completed_peaks = None  # Don't trigger feedback on half rep
        else:
            # عد عادي: كل دورة = عدة
            state["count"] += 1
            rep_completed = True
            print(f"[REP] COUNTED! Total: {state['count']}")

    return state["count"], rep_completed, completed_peaks


def _update_peak_tracking(state, all_angles):
    """Track minimum values for all joints during a rep (used for feedback)."""
    for joint, angle in all_angles.items():
        if joint not in state["peak_angles"]:
            state["peak_angles"][joint] = angle
        else:
            # For most exercises, "peak" = minimum angle (deepest point)
            # We track the minimum seen during this rep
            state["peak_angles"][joint] = min(state["peak_angles"][joint], angle)


def get_last_rep_peaks(exercise_name):
    """Get the peak angles from the last completed rep."""
    if exercise_name in rep_states:
        return rep_states[exercise_name].get("last_rep_peaks")
    return None


def reset_reps(exercise_name):
    """Reset rep count for an exercise."""
    if exercise_name in rep_states:
        rep_states[exercise_name].update({
            "start_reached": False,
            "end_reached": False,
            "count": 0,
            "cooldown": 0,
            "last_angle": None,
            "peak_angles": {},
            "in_rep": False,
            "last_rep_peaks": None,
        })


def get_rep_count(exercise_name):
    """Get current rep count without modifying state."""
    if exercise_name in rep_states:
        return rep_states[exercise_name]["count"]
    return 0
