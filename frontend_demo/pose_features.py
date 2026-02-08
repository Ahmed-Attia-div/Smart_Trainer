import numpy as np

def calculate_angle(a, b, c):
    """
    Calculate angle between three points
    a, b, c: [x, y, z] coordinates
    Returns: angle in degrees
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

def calculate_distance(a, b):
    """Euclidean distance between two points"""
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)

def extract_features(landmarks):
    """
    Extract meaningful features from pose landmarks
    landmarks: array of shape (33, 4) - 33 keypoints
    """
    # Reshape landmarks
    lm = landmarks.reshape(33, 4)
    
    features = []
    
    # Key joint angles
    # Right arm
    right_elbow = calculate_angle(
        lm[12][:3], lm[14][:3], lm[16][:3]  # shoulder-elbow-wrist
    )
    features.append(right_elbow)
    
    # Left arm
    left_elbow = calculate_angle(
        lm[11][:3], lm[13][:3], lm[15][:3]
    )
    features.append(left_elbow)
    
    # Right leg
    right_knee = calculate_angle(
        lm[24][:3], lm[26][:3], lm[28][:3]  # hip-knee-ankle
    )
    features.append(right_knee)
    
    # Left leg
    left_knee = calculate_angle(
        lm[23][:3], lm[25][:3], lm[27][:3]
    )
    features.append(left_knee)
    
    # Hip angle (torso bend)
    right_hip = calculate_angle(
        lm[12][:3], lm[24][:3], lm[26][:3]  # shoulder-hip-knee
    )
    features.append(right_hip)
    
    left_hip = calculate_angle(
        lm[11][:3], lm[23][:3], lm[25][:3]
    )
    features.append(left_hip)
    
    # Shoulder angles
    right_shoulder = calculate_angle(
        lm[24][:3], lm[12][:3], lm[14][:3]  # hip-shoulder-elbow
    )
    features.append(right_shoulder)
    
    left_shoulder = calculate_angle(
        lm[23][:3], lm[11][:3], lm[13][:3]
    )
    features.append(left_shoulder)
    
    # Distances
    # Hand to opposite knee
    right_hand_left_knee = calculate_distance(
        lm[16][:3], lm[25][:3]
    )
    features.append(right_hand_left_knee)
    
    left_hand_right_knee = calculate_distance(
        lm[15][:3], lm[26][:3]
    )
    features.append(left_hand_right_knee)
    
    # Hands distance
    hands_distance = calculate_distance(
        lm[15][:3], lm[16][:3]
    )
    features.append(hands_distance)
    
    # Body center height (hip average y-coordinate)
    body_height = (lm[23][1] + lm[24][1]) / 2
    features.append(body_height)
    
    # Torso width
    torso_width = calculate_distance(
        lm[11][:3], lm[12][:3]
    )
    features.append(torso_width)
    
    # Visibility scores (important for detecting occlusion)
    avg_visibility = np.mean(lm[:, 3])
    features.append(avg_visibility)
    
    return np.array(features)
