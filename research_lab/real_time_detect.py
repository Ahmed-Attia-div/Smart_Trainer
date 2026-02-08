import cv2
import mediapipe as mp
import numpy as np
import pickle
from collections import deque
from feature_engineering import extract_features
import xgboost as xgb


with open('pose_classifier.pkl', 'rb') as f:
    model = pickle.load(f)

with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Temporal smoothing
WINDOW_SIZE = 30  # 1 second at 30fps
pose_buffer = deque(maxlen=WINDOW_SIZE)
prediction_buffer = deque(maxlen=10)

def extract_keypoints(results):
    """Extract pose landmarks"""
    if results.pose_landmarks:
        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            keypoints.extend([landmark.x, landmark.y, 
                            landmark.z, landmark.visibility])
        return np.array(keypoints)
    return np.zeros(33 * 4)

def get_smoothed_prediction(buffer):
    """Mode of recent predictions"""
    if len(buffer) < 5:
        return None
    return max(set(buffer), key=buffer.count)

def main():
    video_path = "../pose based classyfier/squat.mp4"
    cap = cv2.VideoCapture(0)  # Webcam
    
    with mp_pose.Pose(
        min_detection_confidence=0.8,
        min_tracking_confidence=0.7
    ) as pose:
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect pose
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )
                
                # Extract keypoints
                keypoints = extract_keypoints(results)
                pose_buffer.append(keypoints)
                
                # Make prediction when buffer is full
                if len(pose_buffer) == WINDOW_SIZE:
                    # Extract features from window
                    window = np.array(pose_buffer)
                    frame_features = []
                    
                    for frame_poses in window:
                        feats = extract_features(frame_poses)
                        frame_features.append(feats)
                    
                    frame_features = np.array(frame_features)
                    
                    # Aggregate features
                    features = []
                    features.extend(np.mean(frame_features, axis=0))
                    features.extend(np.std(frame_features, axis=0))
                    features.extend(np.max(frame_features, axis=0))
                    features.extend(np.min(frame_features, axis=0))
                    
                    velocities = np.diff(frame_features, axis=0)
                    features.extend(np.mean(velocities, axis=0))
                    features.extend(np.std(velocities, axis=0))
                    
                    features = np.array(features).reshape(1, -1)
                    
                    # Predict
                    pred = model.predict(features)[0]
                    proba = model.predict_proba(features)[0]
                    confidence = proba[pred]
                    
                    # Only add to buffer if confident
                    if confidence > 0.7:
                        prediction_buffer.append(pred)
                    
                    # Get smoothed prediction
                    smoothed_pred = get_smoothed_prediction(
                        prediction_buffer
                    )
                    
                    if smoothed_pred is not None:
                        exercise = label_encoder.inverse_transform(
                            [smoothed_pred]
                        )[0]
                        
                        # Display
                        cv2.putText(
                            image, 
                            f"Exercise: {exercise}", 
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2
                        )
                        cv2.putText(
                            image, 
                            f"Confidence: {confidence:.2%}", 
                            (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2
                        )
            
            # Show frame
            cv2.imshow('Exercise Detection', image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()