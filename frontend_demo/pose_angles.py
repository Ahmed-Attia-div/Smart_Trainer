import cv2
import mediapipe as mp
import numpy as np

from count_reps import update_reps
from exercises_angles import EXERCISE_RULES
from set_manager import update_set, get_set_summary
from audio_feedback import get_rep_feedback, get_set_feedback, get_rest_feedback
from rest_recommendation import recommend_rest_time
from feedback_system import evaluate_rep, detect_view


last_rep_count = {}

def reset_last_reps():
    """Reset local rep tracking for UI updates"""
    last_rep_count.clear()  # استخدم clear() بدل = {} عشان الـ imports تشتغل صح

mp_pose = mp.solutions.pose

# Lazy initialization
_pose_tracker = None

def get_pose():
    global _pose_tracker
    if _pose_tracker is None:
        _pose_tracker = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    return _pose_tracker

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

def draw_point(frame, point, color=(0, 255, 0)):
    cv2.circle(frame, point, 6, color, -1)


    
    



def draw_pose_and_angles(frame, exercise_name=None):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = get_pose().process(image_rgb)

    if not results.pose_landmarks:
        return frame, [], {}  # 🔧 Return consistent tuple (frame, audio_messages, angles)

    h, w, _ = frame.shape
    lm = results.pose_landmarks.landmark

    def p(idx):
        return (int(lm[idx].x * w), int(lm[idx].y * h))

    LEFT_SHOULDER = p(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
    RIGHT_SHOULDER = p(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)

    LEFT_ELBOW = p(mp_pose.PoseLandmark.LEFT_ELBOW.value)
    RIGHT_ELBOW = p(mp_pose.PoseLandmark.RIGHT_ELBOW.value)

    LEFT_WRIST = p(mp_pose.PoseLandmark.LEFT_WRIST.value)
    RIGHT_WRIST = p(mp_pose.PoseLandmark.RIGHT_WRIST.value)

    LEFT_HIP = p(mp_pose.PoseLandmark.LEFT_HIP.value)
    RIGHT_HIP = p(mp_pose.PoseLandmark.RIGHT_HIP.value)

    LEFT_KNEE = p(mp_pose.PoseLandmark.LEFT_KNEE.value)
    RIGHT_KNEE = p(mp_pose.PoseLandmark.RIGHT_KNEE.value)

    LEFT_ANKLE = p(mp_pose.PoseLandmark.LEFT_ANKLE.value)
    RIGHT_ANKLE = p(mp_pose.PoseLandmark.RIGHT_ANKLE.value)

    left_elbow_angle = calculate_angle(LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST)
    right_elbow_angle = calculate_angle(RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST)
    left_shoulder_angle  = calculate_angle(LEFT_HIP, LEFT_SHOULDER, LEFT_ELBOW)
    right_shoulder_angle = calculate_angle(RIGHT_HIP, RIGHT_SHOULDER, RIGHT_ELBOW)
    hip_angle = calculate_angle(LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE)
    left_knee_angle = calculate_angle(LEFT_HIP, LEFT_KNEE, LEFT_ANKLE)
    right_knee_angle = calculate_angle(
        p(mp_pose.PoseLandmark.RIGHT_HIP.value),
        RIGHT_KNEE,
        RIGHT_ANKLE
    )
    

    angles = {
        "elbow": (left_elbow_angle + right_elbow_angle) / 2,
        "hip": hip_angle,
        "knee": (left_knee_angle + right_knee_angle) / 2,
        "shoulder": (left_shoulder_angle + right_shoulder_angle) / 2
    }

    # Collect audio messages
    audio_messages = []



    points_to_draw = [
        LEFT_SHOULDER, RIGHT_SHOULDER,
        LEFT_ELBOW, RIGHT_ELBOW,
        LEFT_HIP, LEFT_KNEE, RIGHT_KNEE
    ]
    for pt in points_to_draw:
        draw_point(frame, pt)


    cv2.putText(frame, f"{int(left_elbow_angle)} degrees",
                (LEFT_ELBOW[0]+10, LEFT_ELBOW[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"{int(right_elbow_angle)} degrees",
                (RIGHT_ELBOW[0]+10, RIGHT_ELBOW[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, f"{int(hip_angle)} degrees",
                (LEFT_HIP[0]+10, LEFT_HIP[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, f"{int(left_knee_angle)} degrees",
                (LEFT_KNEE[0]+10, LEFT_KNEE[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"{int(right_knee_angle)} degrees",
                (RIGHT_KNEE[0]+10, RIGHT_KNEE[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    



    cv2.putText(frame, f"{int(left_shoulder_angle)} degrees",
                (LEFT_SHOULDER[0]+10, LEFT_SHOULDER[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"{int(right_shoulder_angle)} degrees",
                (RIGHT_SHOULDER[0]+10, RIGHT_SHOULDER[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


            



    current_count = 0
    rep_detected = False
    event = None
    
    # Build landmarks dict for view detection
    landmarks = {
        "left_shoulder": LEFT_SHOULDER,
        "right_shoulder": RIGHT_SHOULDER,
        "left_hip": LEFT_HIP,
        "right_hip": RIGHT_HIP,
    }

    if exercise_name and exercise_name in EXERCISE_RULES:
        # Pass ALL angles to update_reps for comprehensive tracking
        current_count, rep_just_completed, peak_angles = update_reps(exercise_name, angles)
        
        rep_is_good = None  # Default state

        last = last_rep_count.get(exercise_name, 0)
        if current_count > last:
            rep_detected = True
            
            # NEW: Evaluate form using feedback rules on completed rep
            rep_is_good = True  # Assume good until proven bad
            
            if peak_angles:
                view = detect_view(landmarks)
                form_feedback = evaluate_rep(exercise_name, view, peak_angles)
                if form_feedback:
                    rep_is_good = False
                    for msg in form_feedback:
                        audio_messages.append(msg)
                    print(f"[FEEDBACK] Bad form detected: {form_feedback}")
                else:
                    print(f"[FEEDBACK] Good rep!")
            
            print(f"[REP DETECTED] good={rep_is_good}")

            last_rep_count[exercise_name] = current_count
        
        # 🔥 DEBUG for Bench Press
        if exercise_name == "bench press":
            print(f"🔍 DEBUG BENCH: {angles}")

        state, event = update_set(
            exercise_name=exercise_name,
            rep_detected=rep_detected,
            rep_is_good=rep_is_good
        )

        if event["rep_completed"]:
            msg = get_rep_feedback(event["rep_good"])
            if msg:
                audio_messages.append(msg)

        if event["set_completed"]:
            msg = get_set_feedback(event["set_quality"])
            if msg:
                audio_messages.append(msg)
                
            rest_seconds = recommend_rest_time(event["set_quality"])
            msg_rest = get_rest_feedback(rest_seconds)
            if msg_rest:
                audio_messages.append(msg_rest)

            cv2.putText(
                frame,
                f"Rest: {rest_seconds}s",
                (25, 320),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 200, 255),
                2   
            )


    summary = get_set_summary(exercise_name)

    cv2.putText(frame, summary,
            (25, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9, (0, 255, 200), 2)

    # 🆕 Rep Quality Score Display - DISABLED
    # if exercise_name:
    #     quality_result = calculate_rep_score(exercise_name, angles)
    #     if quality_result["score"] > 0:
    #         score_text = format_score_text(quality_result)
    #         score_color = get_score_color(quality_result["score"])
    #         # Moved to 360 to avoid overlap
    #         cv2.putText(frame, score_text,
    #                     (25, 360),
    #                     cv2.FONT_HERSHEY_SIMPLEX,
    #                     0.8, score_color, 2)
    #         # print(f"🎨 Drawing Score: {score_text}") # Debug print


    return frame, audio_messages, angles

