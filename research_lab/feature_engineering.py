import numpy as np
import pandas as pd

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

def create_temporal_features(df, window_size=30):
    """
    Create features from sequence of frames
    window_size: number of frames to look back (1 second at 30fps)
    """
    temporal_features = []
    labels = []
    
    for label in df['label'].unique():
        label_data = df[df['label'] == label]
        
        # Get raw pose data (columns 0-131 are the 33*4 keypoints)
        pose_cols = [col for col in df.columns 
                     if col not in ['label', 'frame']]
        poses = label_data[pose_cols].values
        
        # Sliding window
        for i in range(len(poses) - window_size):
            window = poses[i:i+window_size]
            
            # Extract features for each frame in window
            frame_features = []
            for frame_poses in window:
                feats = extract_features(frame_poses)
                frame_features.append(feats)
            
            frame_features = np.array(frame_features)
            
            # Aggregate temporal features
            features = []
            
            # Statistical features
            features.extend(np.mean(frame_features, axis=0))
            features.extend(np.std(frame_features, axis=0))
            features.extend(np.max(frame_features, axis=0))
            features.extend(np.min(frame_features, axis=0))
            
            # Velocity (change over time)
            velocities = np.diff(frame_features, axis=0)
            features.extend(np.mean(velocities, axis=0))
            features.extend(np.std(velocities, axis=0))
            
            temporal_features.append(features)
            labels.append(label)
    
    return np.array(temporal_features), np.array(labels)

# Main processing
def main():
    # Load raw poses
    df = pd.read_csv('data/processed/raw_poses.csv')
    
    print("Creating temporal features...")
    X, y = create_temporal_features(df, window_size=30)
    
    # Save processed data
    np.save('data/processed/X.npy', X)
    np.save('data/processed/y.npy', y)
    
    print(f"Feature shape: {X.shape}")
    print(f"Labels shape: {y.shape}")

if __name__ == "__main__":
    main()