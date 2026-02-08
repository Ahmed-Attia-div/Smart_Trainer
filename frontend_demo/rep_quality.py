"""
Rep Quality Score Module (Advanced)
===================================
Rates rep quality based on Range of Motion (ROM) and Stability.

Algorithm:
1. Compare current angles with REQUIRED ROM (Start & End points).
2. Score is based on how much of the full range was achieved.
3. Penalize for "Cheating" (moving other joints excessively).
"""

from exercises_angles import EXERCISE_RULES

def calculate_rep_score(exercise_name: str, angles: dict) -> dict:
    """
    Calculate professional quality score based on ROM.
    
    Args:
        exercise_name: Name of exercise
        angles: Dict of {joint: current_angle}
        
    Returns:
        Dict with score (0-100) and grade.
    """
    exercise_lower = exercise_name.lower()
    
    if exercise_lower not in EXERCISE_RULES:
        return {"score": 0, "grade": "?", "details": {}}
    
    rules = EXERCISE_RULES[exercise_lower]
    
    # Identify primary moving joint (e.g., knee for squat)
    primary_joint = list(rules.keys())[0]
    
    if primary_joint not in angles or angles[primary_joint] is None:
        return {"score": 0, "grade": "?", "details": {}}
    
    current_angle = angles[primary_joint]
    
    # Get ROM limits from rules
    # We want to check if the user is reaching the "Peak" of the movement
    # For Squat: Peak is Deep (Low angle)
    # For Pull Up: Peak is Up (Low angle)
    # For Push Up: Peak is Down (Low angle)
    
    constraints = rules[primary_joint]
    min_limit = constraints.get("min")
    max_limit = constraints.get("max")
    
    if min_limit is None or max_limit is None:
        return {"score": 0, "grade": "?"}
    
    # Calculate "Depth" or "Peak" score
    # We assume the user is trying to reach the challenging part of the ROM
    
    # Case 1: Target is MIN angle (Flexion - e.g., Squat, Bicep Curl)
    # We reward getting closer to min_limit (or lower)
    dist_to_min = abs(current_angle - min_limit)
    score_min = max(0, 100 - (dist_to_min * 2.5))  # Penalty factor
    
    # Case 2: Target is MAX angle (Extension - e.g., Deadlift lockout)
    # We reward getting closer to max_limit
    dist_to_max = abs(current_angle - max_limit)
    score_max = max(0, 100 - (dist_to_max * 2.5))
    
    # Determine which phase user is in
    # This is a simplification: we take the HIGHER score, assuming user is at peak
    raw_score = max(score_min, score_max)
    
    # 🆕 Stability Bonus/Penalty (Check secondary joints)
    stability_penalty = 0
    
    # Check "hip" stability for upper body exercises
    if "hip" in rules and "hip" in angles:
        hip_target = rules["hip"].get("target")
        hip_tolerance = rules["hip"].get("tolerance", 20)
        
        if hip_target:
            hip_dev = abs(angles["hip"] - hip_target)
            if hip_dev > hip_tolerance:
                stability_penalty += (hip_dev - hip_tolerance) * 1.5
    
    final_score = raw_score - stability_penalty
    final_score = max(0, min(100, final_score))  # Clamp 0-100
    
    # Grade
    if final_score >= 90: grade = "A+"
    elif final_score >= 85: grade = "A"
    elif final_score >= 75: grade = "B"
    elif final_score >= 65: grade = "C"
    elif final_score >= 50: grade = "D"
    else: grade = "F"
    
    return {
        "score": round(final_score, 1),
        "grade": grade,
        "details": {
            "primary": primary_joint,
            "angle": round(current_angle, 1),
            "stability_penalty": round(stability_penalty, 1)
        }
    }


def get_score_color(score: float) -> tuple:
    if score >= 85: return (0, 255, 0)      # Green
    elif score >= 70: return (0, 255, 200)  # Cyan
    elif score >= 50: return (0, 165, 255)  # Orange
    return (0, 0, 255)                      # Red


def format_score_text(result: dict) -> str:
    return f"Form: {result['score']:.0f}% ({result['grade']})"
