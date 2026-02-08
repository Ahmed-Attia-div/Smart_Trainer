import cv2
import numpy as np
import mediapipe as mp
import pickle
import os
import xgboost as xgb
from collections import deque
from pose_features import extract_features

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
POSE_MODEL_PATH = os.path.join(CURRENT_DIR, 'production model', 'pose_classifier.pkl')
LABEL_ENCODER_PATH = os.path.join(CURRENT_DIR, 'production model', 'label_encoder.pkl')

# Global Lazy Variables
_pose_detector = None
model = None
label_encoder = None

def get_models():
    """Lazy load models"""
    global model, label_encoder
    if model is None:
        try:
            with open(POSE_MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            with open(LABEL_ENCODER_PATH, 'rb') as f:
                label_encoder = pickle.load(f)
            print(f"[INIT] Loaded XGBoost model from {POSE_MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to load models: {e}")
            model = None
            label_encoder = None
    return model, label_encoder

def get_pose_detector():
    """Lazy load MediaPipe"""
    global _pose_detector
    if _pose_detector is None:
        _pose_detector = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    return _pose_detector

# Configuration
WINDOW_SIZE = 30  # 30 frames smoothing
CONFIDENCE_THRESHOLD = 0.75

def init_detector_state():
    """Returns the initial state for a session"""
    # Ensure models are loaded when session starts
    get_models() 
    return {
        "pose_buffer": deque(maxlen=WINDOW_SIZE),
        "prediction_buffer": deque(maxlen=10),
        "last_prediction": None,
        "locked": False
    }

def get_smoothed_prediction(buffer):
    """Mode of recent predictions"""
    if len(buffer) < 3:
        return None
    return max(set(buffer), key=buffer.count)

def detect_exercise(frame, state):
    """
    Main detection function called by api_server.py
    Returns: (exercise_name, confidence)
    """
    # Ensure models are loaded
    local_model, local_encoder = get_models()
    
    if local_model is None or state["locked"]:
        return None, 0.0

    pose_detector = get_pose_detector()

    # 1. Flip & Color Convert
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 2. Process Pose
    results = pose_detector.process(image_rgb)
    
    if not results.pose_landmarks:
        return None, 0.0
        
    # 3. Extract Keypoints (33 * 4)
    keypoints = []
    for landmark in results.pose_landmarks.landmark:
        keypoints.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
    
    keypoints = np.array(keypoints)
    state["pose_buffer"].append(keypoints)
    
    # 4. Predict if buffer is full
    if len(state["pose_buffer"]) == WINDOW_SIZE:
        # Create sliding window batch
        window = np.array(state["pose_buffer"])
        
        # Extract features for each frame in window
        frame_features = []
        for frame_poses in window:
            feats = extract_features(frame_poses)
            frame_features.append(feats)
        
        frame_features = np.array(frame_features)
        
        # Aggregate temporal features
        features = []
        features.extend(np.mean(frame_features, axis=0))
        features.extend(np.std(frame_features, axis=0))
        features.extend(np.max(frame_features, axis=0))
        features.extend(np.min(frame_features, axis=0))
        
        velocities = np.diff(frame_features, axis=0)
        features.extend(np.mean(velocities, axis=0))
        features.extend(np.std(velocities, axis=0))
        
        # Reshape for XGBoost
        features = np.array(features).reshape(1, -1)
        
        # Predict
        try:
            pred_idx = local_model.predict(features)[0]
            proba = local_model.predict_proba(features)[0]
            confidence = proba[pred_idx]
            
            # Update prediction buffer
            if confidence > CONFIDENCE_THRESHOLD:
                state["prediction_buffer"].append(pred_idx)
            
            # Smooth result
            smoothed_idx = get_smoothed_prediction(state["prediction_buffer"])
            
            if smoothed_idx is not None:
                exercise_name = local_encoder.inverse_transform([smoothed_idx])[0]
                
                print(f"[XGBOOST] {exercise_name} ({confidence:.1%})")
                
                if confidence > 0.85:
                    state["locked"] = True # Auto-lock if very confident
                    return exercise_name, confidence

                return exercise_name, confidence
                
        except Exception as e:
            print(f"[PREDICT ERROR] {e}")
            return None, 0.0

    return None, 0.0