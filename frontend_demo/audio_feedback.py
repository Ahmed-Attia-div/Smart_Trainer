"""
Audio Feedback Module (Text Generator)
=====================================
Generates feedback text strings to be sent to the client.
NO pyttsx3 dependency. NO threads. Pure logic.
"""

import time
import random

# Cooldowns
_last_form_time = 0
_last_rep_time = 0
FORM_COOLDOWN = 8.0   # Seconds between form corrections
REP_COOLDOWN = 3.0    # Seconds between rep encouragements

# Phrases
GOOD_FORM_PHRASES = [
    "Nice form",
    "Good control",
    "Clean movement",
    "Strong form",
    "That's solid",
    "Perfect",
    "Keep it up"
]

REP_PHRASES = [
    "Good rep",
    "Nice one",
    "Keep going",
    "Strong"
]

def get_form_feedback(joint_feedback: dict) -> str:
    """
    Get form feedback message if cooldown passed.
    Returns None if no message should be spoken.
    """
    global _last_form_time
    
    if not joint_feedback:
        return None
    
    now = time.time()
    if now - _last_form_time < FORM_COOLDOWN:
        return None
    
    wrong_msgs = []
    for msg in joint_feedback.values():
        if "good" not in msg.lower():
            wrong_msgs.append(msg)
    
    if wrong_msgs:
        _last_form_time = now
        return random.choice(wrong_msgs)
    
    # Optional: Encourage good form periodically?
    # For now, let's keep it quiet unless there's an issue
    return None


def get_rep_feedback(rep_good: bool) -> str:
    """Get rep completion message."""
    global _last_rep_time
    
    now = time.time()
    if now - _last_rep_time < REP_COOLDOWN:
        return None
    
    if rep_good:
        _last_rep_time = now
        return random.choice(REP_PHRASES)
    
    return None


def get_set_feedback(set_quality: str) -> str:
    """Get set completion message."""
    if set_quality == "excellent":
        return "Excellent set!"
    elif set_quality == "good":
        return "Good set!"
    else:
        return "Focus on form next set"


def get_rest_feedback(seconds: int) -> str:
    """Get rest time message."""
    if seconds >= 90:
        return "Take ninety seconds rest"
    elif seconds >= 60:
        return "Rest for one minute"
    else:
        return "Take thirty seconds rest"


# للتجربة
if __name__ == "__main__":
    print(get_set_feedback("excellent"))
    print(get_rest_feedback(30))
