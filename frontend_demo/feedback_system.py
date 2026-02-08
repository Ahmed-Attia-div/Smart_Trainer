"""
Feedback System
===============
Provides angle-aware form feedback based on pre-analyzed rules from feedback_rules.json.

Key Functions:
- detect_view(): Determines camera angle (front/side/45) from landmarks
- evaluate_rep(): Checks if rep violates any form rules
- get_feedback_messages(): Returns appropriate voice messages
"""

import json
import os
import math

# ========== LOAD RULES ==========
RULES_FILE = os.path.join(os.path.dirname(__file__), "feedback_rules.json")
_feedback_rules = {}

def load_rules():
    """Load feedback rules from JSON file."""
    global _feedback_rules
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            _feedback_rules = json.load(f)
        print(f"[FEEDBACK] Loaded rules for {len(_feedback_rules)} exercises")
    else:
        print(f"[FEEDBACK] Warning: {RULES_FILE} not found!")
    return _feedback_rules

def get_rules():
    """Get loaded rules (loads if not already loaded)."""
    global _feedback_rules
    if not _feedback_rules:
        load_rules()
    return _feedback_rules


# ========== VIEW DETECTION ==========
def detect_view(landmarks):
    """
    Detect camera view based on shoulder width ratio.
    
    Args:
        landmarks: Dictionary with "left_shoulder" and "right_shoulder" as (x, y) tuples.
                   Also needs "left_hip" and "right_hip" for body height reference.
    
    Returns:
        str: "front", "side", or "45"
    """
    if not landmarks:
        return "side"  # Default fallback
    
    try:
        left_shoulder = landmarks.get("left_shoulder")
        right_shoulder = landmarks.get("right_shoulder")
        left_hip = landmarks.get("left_hip")
        right_hip = landmarks.get("right_hip")
        
        if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
            return "side"
        
        # Calculate shoulder width (horizontal distance)
        shoulder_width = abs(right_shoulder[0] - left_shoulder[0])
        
        # Calculate body height (vertical distance from shoulder to hip)
        shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_center_y = (left_hip[1] + right_hip[1]) / 2
        body_height = abs(hip_center_y - shoulder_center_y)
        
        if body_height < 10:  # Avoid division by zero
            return "side"
        
        # Ratio of shoulder width to body height
        ratio = shoulder_width / body_height
        
        # Classification thresholds (based on empirical testing)
        # Front view: shoulders appear widest
        # Side view: shoulders appear narrowest
        # 45 degree: somewhere in between
        
        if ratio > 0.8:
            view = "front"
        elif ratio < 0.3:
            view = "side"
        else:
            view = "45"
        
        return view
        
    except Exception as e:
        print(f"[FEEDBACK] View detection error: {e}")
        return "side"


# ========== FEEDBACK EVALUATION ==========
def evaluate_rep(exercise_name, view, peak_angles):
    """
    Evaluate a completed rep against the rules for this exercise/view.
    
    Args:
        exercise_name: Name of exercise (e.g., "bench press")
        view: Camera view ("front", "side", "45")
        peak_angles: Dictionary of joint angles at the peak of the rep
                     e.g., {"elbow": 85, "shoulder": 45, "knee": 90, "hip": 120}
    
    Returns:
        List of feedback messages (strings) for any violated rules.
        Empty list if form is good.
    """
    rules = get_rules()
    messages = []
    
    # Normalize exercise name
    exercise_key = exercise_name.lower()
    
    if exercise_key not in rules:
        return []  # No rules for this exercise
    
    exercise_rules = rules[exercise_key]
    
    if view not in exercise_rules:
        # Try to fall back to another view if current view not available
        available_views = list(exercise_rules.keys())
        if not available_views:
            return []
        view = available_views[0]  # Use first available
    
    view_rules = exercise_rules.get(view, [])
    
    for rule in view_rules:
        joint = rule.get("joint")
        threshold = rule.get("threshold")
        condition = rule.get("condition")
        message = rule.get("message")
        
        if joint not in peak_angles:
            continue
        
        current_value = peak_angles[joint]
        
        # Check if rule is violated
        violated = False
        if condition == ">" and current_value > threshold:
            violated = True
        elif condition == "<" and current_value < threshold:
            violated = True
        
        if violated:
            messages.append(message)
            print(f"[FEEDBACK] Rule violated: {joint} {condition} {threshold} (got {current_value:.1f}) -> {message}")
    
    return messages


def get_relevant_joints(exercise_name):
    """
    Get list of joints that have rules for this exercise.
    Useful for filtering which joints to track.
    """
    rules = get_rules()
    exercise_key = exercise_name.lower() if exercise_name else ""
    
    if exercise_key not in rules:
        return ["elbow", "shoulder", "knee", "hip"]  # Default all
    
    joints = set()
    for view_rules in rules[exercise_key].values():
        for rule in view_rules:
            joints.add(rule.get("joint"))
    
    return list(joints) if joints else ["elbow", "shoulder", "knee", "hip"]


# Initialize on import
load_rules()
