"""
Injury Prevention Alerts Module
================================
Warns users when joint angles reach dangerous limits.

IMPORTANT: Joint names MUST match those in exercises_angles.py:
- elbow, hip, knee, shoulder
"""

# 🚨 مناطق الخطر لكل تمرين
# Format: joint: (min_safe, max_safe, warning_message)
# لو الزاوية أقل من min_safe أو أكبر من max_safe = خطر

DANGER_ZONES = {
    # === ARMS ===
    "barbell biceps curl": {
        "elbow": {
            "min": 20,   # ثني الكوع الزائد = ضغط على المفصل
            "max": None,
            "warning": "⚠️ Don't over-curl! Elbow stress"
        }
    },
    
    "hammer curl": {
        "elbow": {
            "min": 20,
            "max": None,
            "warning": "⚠️ Don't over-curl! Elbow stress"
        }
    },
    
    # === CHEST ===
    "bench press": {
        "elbow": {
            "min": 50,   # كوع منخفض جداً = ضغط على الكتف
            "max": None,
            "warning": "⚠️ Elbows too low! Shoulder stress"
        }
    },
    
    "incline bench press": {
        "elbow": {
            "min": 40,
            "max": None,
            "warning": "⚠️ Don't go too deep! Shoulder risk"
        }
    },
    
    "decline bench press": {
        "elbow": {
            "min": 40,
            "max": None,
            "warning": "⚠️ Don't go too deep! Shoulder risk"
        }
    },
    
    "chest fly machine": {
        "shoulder": {
            "min": 20,   # فتح الذراعين أكتر من اللازم
            "max": None,
            "warning": "⚠️ Arms too wide! Shoulder strain"
        }
    },
    
    # === SHOULDERS ===
    "shoulder press": {
        "elbow": {
            "min": 15,   # Only warn if EXTREMELY compressed (<15)
            "max": None,
            "warning": "⚠️ Too deep! Shoulder risk"
        }
    },
    
    "lateral raises": {
        "shoulder": {
            "min": None,
            "max": 100,  # رفع الذراع فوق الكتف = ضغط
            "warning": "⚠️ Don't raise above shoulder level!"
        }
    },
    
    # === BACK ===
    "lat pulldown": {
        "elbow": {
            "min": 30,
            "max": None,
            "warning": "⚠️ Don't over-pull! Shoulder strain"
        }
    },
    
    "pull up": {
        "elbow": {
            "min": 40,
            "max": None,
            "warning": "⚠️ Don't over-pull! Shoulder strain"
        }
    },
    
    "t bar row": {
        "hip": {
            "min": 60,   # الظهر منحني أكتر من اللازم
            "max": None,
            "warning": "⚠️ Back too bent! Lower back risk"
        }
    },
    
    # === TRICEPS ===
    "tricep dips": {
        "elbow": {
            "min": 50,
            "max": None,
            "warning": "⚠️ Too deep! Shoulder risk"
        }
    },
    
    "tricep pushdown": {
        "elbow": {
            "min": 80,
            "max": None,
            "warning": "⚠️ Don't over-extend!"
        }
    },
    
    # === CHEST/CORE ===
    "push up": {
        "elbow": {
            "min": 50,
            "max": None,
            "warning": "⚠️ Too deep! Watch your shoulders"
        }
    },
    
    "plank": {
        "hip": {
            "min": 155,  # الـ hip لازم يكون مفرود
            "max": None,
            "warning": "⚠️ Keep your back straight!"
        }
    },
    
    # === LEGS ===
    "squat": {
        "knee": {
            "min": 45,   # ركبة منحنية أكتر من اللازم
            "max": None,
            "warning": "⚠️ Knee too deep! Joint risk"
        },
        "hip": {
            "min": 40,
            "max": None,
            "warning": "⚠️ Hip too low! Lower back risk"
        }
    },
    
    "deadlift": {
        "hip": {
            "min": 70,   # ظهر منحني جداً
            "max": None,
            "warning": "⚠️ Back too bent! Spine risk"
        }
    },
    
    "romanian deadlift": {
        "hip": {
            "min": 55,
            "max": None,
            "warning": "⚠️ Lower back at risk! Don't go too low"
        }
    },
    
    "hip thrust": {
        "hip": {
            "min": 70,
            "max": None,
            "warning": "⚠️ Don't over-extend!"
        }
    },
    
    "leg extension": {
        "knee": {
            "min": None,
            "max": 175,  # الركبة مش لازم تتمد بالكامل
            "warning": "⚠️ Don't lock knees fully!"
        }
    },
    
    "leg raises": {
        "hip": {
            "min": 60,
            "max": None,
            "warning": "⚠️ Don't swing! Control the movement"
        }
    },
    
    # === CORE ===
    "russian twist": {
        "shoulder": {  # ✅ صحيح - Russian Twist بيستخدم shoulder
            "min": None,
            "max": 50,   # لو اللفة كبيرة أوي ممكن تأذي الظهر
            "warning": "⚠️ Don't twist too far! Spine risk"
        }
    }
}


def check_injury_risk(exercise_name: str, angles: dict) -> list:
    """
    Check if current angles are in danger zones.
    
    Args:
        exercise_name: Name of the exercise
        angles: Dict of {joint: angle_value}
        
    Returns:
        List of warning messages (empty if safe)
    """
    warnings = []
    
    exercise_lower = exercise_name.lower()
    
    if exercise_lower not in DANGER_ZONES:
        return warnings
    
    danger_rules = DANGER_ZONES[exercise_lower]
    
    for joint, limits in danger_rules.items():
        if joint not in angles:
            continue
            
        angle = angles[joint]
        if angle is None:
            continue
        
        min_safe = limits.get("min")
        max_safe = limits.get("max")
        warning_msg = limits.get("warning", "⚠️ Dangerous angle!")
        
        # Check if below minimum safe angle
        if min_safe is not None and angle < min_safe:
            warnings.append({
                "joint": joint,
                "angle": angle,
                "limit": min_safe,
                "type": "too_low",
                "message": warning_msg
            })
        
        # Check if above maximum safe angle
        if max_safe is not None and angle > max_safe:
            warnings.append({
                "joint": joint,
                "angle": angle,
                "limit": max_safe,
                "type": "too_high",
                "message": warning_msg
            })
    
    return warnings


def get_warning_color(warning_type: str) -> tuple:
    """Get BGR color for warning display."""
    if warning_type == "too_low":
        return (0, 0, 255)  # Red
    elif warning_type == "too_high":
        return (0, 165, 255)  # Orange
    return (0, 255, 255)  # Yellow default


# للتجربة
if __name__ == "__main__":
    # Test squat
    test_angles = {"knee": 40, "hip": 85}
    warnings = check_injury_risk("squat", test_angles)
    
    if warnings:
        for w in warnings:
            print(f"🚨 {w['message']} (angle: {w['angle']}°, limit: {w['limit']}°)")
    else:
        print("✅ All angles are safe!")
    
    # Test russian twist
    test_angles2 = {"shoulder": 55, "hip": 120}
    warnings2 = check_injury_risk("russian twist", test_angles2)
    
    if warnings2:
        for w in warnings2:
            print(f"🚨 {w['message']} (angle: {w['angle']}°)")
    else:
        print("✅ Russian twist angles are safe!")
