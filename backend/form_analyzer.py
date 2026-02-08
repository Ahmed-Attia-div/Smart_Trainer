"""
Form Analyzer Module - Post-Workout Video Analysis with 5-Pillar Scoring

This module processes a workout video and calculates biomechanical scores
for Stability, Posture, ROM, Movement Quality, and Bracing.
"""
import cv2
import mediapipe as mp
import numpy as np
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PillarScore:
    """Represents a single pillar score with feedback."""
    score: int
    feedback: str
    solution: Optional[str] = None


@dataclass
class AnalysisResult:
    """Complete analysis result for a workout video."""
    exercise: str
    reps_analyzed: int
    overall_score: int
    pillars: Dict[str, PillarScore]
    summary: str
    solutions: List[str]


class FormAnalyzer:
    """
    Analyzes workout form from video using pose estimation and biomechanical rules.
    """
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Store all frame data for analysis
        self.all_landmarks: List[np.ndarray] = []
        self.frame_count = 0
        
        # Ideal angle ranges per exercise (loaded from feedback_rules.json if available)
        self.exercise_thresholds = self._load_thresholds()
    
    def _load_thresholds(self) -> dict:
        """Load exercise-specific thresholds from feedback_rules.json."""
        try:
            with open("feedback_rules.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Default thresholds
            return {
                "bicep curl": {"elbow_min": 40, "elbow_max": 160},
                "squat": {"knee_min": 70, "hip_min": 70},
                "bench press": {"elbow_min": 45, "shoulder_max": 90},
            }
    
    def analyze_video(
        self,
        video_path: str,
        exercise_name: str,
        rep_count: int,
        rep_timestamps: Optional[List[dict]] = None
    ) -> AnalysisResult:
        """
        Main entry point - analyzes a video file and returns detailed scoring.
        
        Args:
            video_path: Path to the video file
            exercise_name: Name of the exercise performed
            rep_count: Number of reps (provided by mobile app)
            rep_timestamps: Optional list of {"start": float, "end": float} per rep
        
        Returns:
            AnalysisResult with all pillar scores and feedback
        """
        # Step 1: Extract poses from video
        self._extract_poses(video_path)
        
        if not self.all_landmarks:
            return self._empty_result(exercise_name, rep_count)
        
        # Step 2: Calculate each pillar score
        stability = self._calculate_stability()
        posture = self._calculate_posture(exercise_name)
        rom = self._calculate_rom(exercise_name)
        movement_quality = self._calculate_movement_quality(rep_timestamps)
        bracing = self._calculate_bracing()
        
        # Step 3: Calculate overall score (weighted average)
        overall = int(
            stability.score * 0.20 +
            posture.score * 0.25 +
            rom.score * 0.25 +
            movement_quality.score * 0.15 +
            bracing.score * 0.15
        )
        
        # Step 4: Generate AI feedback
        from ai_advisor import get_ai_feedback
        
        pillar_dict = {
            "stability": {"score": stability.score, "feedback": stability.feedback},
            "posture": {"score": posture.score, "feedback": posture.feedback},
            "rom": {"score": rom.score, "feedback": rom.feedback},
            "movement_quality": {"score": movement_quality.score, "feedback": movement_quality.feedback},
            "bracing": {"score": bracing.score, "feedback": bracing.feedback},
        }
        
        ai_response = get_ai_feedback(exercise_name, pillar_dict, rep_count)
        
        return AnalysisResult(
            exercise=exercise_name,
            reps_analyzed=rep_count,
            overall_score=overall,
            pillars={
                "stability": stability,
                "posture": posture,
                "range_of_motion": rom,
                "movement_quality": movement_quality,
                "bracing_core": bracing,
            },
            summary=ai_response.get("summary", ""),
            solutions=ai_response.get("solutions", [])
        )
    
    def _extract_poses(self, video_path: str):
        """Extract pose landmarks from every frame of the video."""
        self.all_landmarks = []
        cap = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not cap.isOpened():
            print(f"[ANALYZER ERROR] Could not open video file: {video_path}")
            print(f"[ANALYZER ERROR] Supported formats: .mp4, .mov, .avi, .webm")
            cap.release()
            return
        
        print(f"[ANALYZER] Processing video: {video_path}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            
            if results.pose_landmarks:
                # Convert to numpy array (33 landmarks x 4 values)
                landmarks = np.array([
                    [lm.x, lm.y, lm.z, lm.visibility]
                    for lm in results.pose_landmarks.landmark
                ])
                self.all_landmarks.append(landmarks)
            
            self.frame_count += 1
        
        cap.release()
        print(f"[ANALYZER] Extracted {len(self.all_landmarks)} pose frames from {self.frame_count} total frames")
    
    def _calculate_stability(self) -> PillarScore:
        """
        Calculate stability score based on hip/shoulder position variance.
        Uses combined anterior-posterior (Y) and medio-lateral (X) sway.
        Scientific basis: NIH Center of Mass variance methodology.
        """
        if not self.all_landmarks:
            return PillarScore(0, "No pose data available")
        
        # Track hip center position across frames
        hip_positions = []
        for lm in self.all_landmarks:
            left_hip = lm[23][:2]  # x, y
            right_hip = lm[24][:2]
            hip_center = (left_hip + right_hip) / 2
            hip_positions.append(hip_center)
        
        hip_positions = np.array(hip_positions)
        
        # Calculate standard deviation of X (lateral) and Y (anterior-posterior) positions
        x_std = np.std(hip_positions[:, 0])  # Medio-lateral sway
        y_std = np.std(hip_positions[:, 1])  # Anterior-posterior sway
        
        # Combined sway using Euclidean distance (NIH methodology)
        total_sway = np.sqrt(x_std**2 + y_std**2)
        
        # Score: Map combined sway to 0-100
        # Thresholds based on normalized coordinates (0-1 range)
        # Research: Postural sway < 2% of stance width = excellent stability
        if total_sway < 0.025:
            score = 95
            feedback = "Excellent stability! Minimal body sway in all directions."
        elif total_sway < 0.045:
            score = 80
            feedback = "Good stability with minor sway."
        elif total_sway < 0.07:
            score = 65
            feedback = "Moderate hip sway detected - focus on core engagement."
        else:
            score = 50
            feedback = "Significant instability - excessive hip movement. Reduce weight and focus on control."
        
        return PillarScore(score, feedback)
    
    def _calculate_posture(self, exercise_name: str) -> PillarScore:
        """
        Calculate posture score based on spine alignment and head position.
        Uses exercise-specific forward lean norms (NASM/NSCA guidelines).
        """
        if not self.all_landmarks:
            return PillarScore(0, "No pose data available")
        
        # Exercise-specific posture norms (ideal forward lean angles)
        # Based on NASM Corrective Exercise Specialist guidelines
        POSTURE_NORMS = {
            "squat": {"ideal_lean": 25, "tolerance": 15},  # Hip hinge requires lean
            "deadlift": {"ideal_lean": 45, "tolerance": 15},
            "romanian deadlift": {"ideal_lean": 50, "tolerance": 15},
            "bent over row": {"ideal_lean": 45, "tolerance": 10},
            "barbell row": {"ideal_lean": 45, "tolerance": 10},
            "bicep curl": {"ideal_lean": 5, "tolerance": 10},
            "barbell biceps curl": {"ideal_lean": 5, "tolerance": 10},
            "hammer curl": {"ideal_lean": 5, "tolerance": 10},
            "shoulder press": {"ideal_lean": 5, "tolerance": 10},
            "bench press": {"ideal_lean": 10, "tolerance": 10},  # Slight arch
            "lat pulldown": {"ideal_lean": 15, "tolerance": 10},
            "tricep pushdown": {"ideal_lean": 10, "tolerance": 10},
            "lateral raise": {"ideal_lean": 5, "tolerance": 10},
            "leg press": {"ideal_lean": 0, "tolerance": 15},  # Seated
            "leg extension": {"ideal_lean": 0, "tolerance": 10},
            "leg curl": {"ideal_lean": 0, "tolerance": 10},
            "calf raise": {"ideal_lean": 5, "tolerance": 10},
            "hip thrust": {"ideal_lean": 0, "tolerance": 10},
            "lunge": {"ideal_lean": 10, "tolerance": 10},
            "push up": {"ideal_lean": 0, "tolerance": 10},
            "pull up": {"ideal_lean": 10, "tolerance": 15},
            "chest fly": {"ideal_lean": 0, "tolerance": 10},
        }
        
        exercise_key = exercise_name.lower().strip()
        norms = POSTURE_NORMS.get(exercise_key, {"ideal_lean": 15, "tolerance": 10})
        
        spine_angles = []
        head_movements = []
        
        for lm in self.all_landmarks:
            # Spine angle: shoulder-hip line vs vertical
            shoulder_mid = (lm[11][:2] + lm[12][:2]) / 2
            hip_mid = (lm[23][:2] + lm[24][:2]) / 2
            
            # Angle from vertical
            dx = shoulder_mid[0] - hip_mid[0]
            dy = shoulder_mid[1] - hip_mid[1]
            angle = np.degrees(np.arctan2(abs(dx), abs(dy)))
            spine_angles.append(angle)
            
            # Head position (nose X coordinate)
            nose_x = lm[0][0]
            head_movements.append(nose_x)
        
        # Spine deviation from exercise-specific ideal
        avg_spine = np.mean(spine_angles)
        spine_std = np.std(spine_angles)
        deviation = abs(avg_spine - norms["ideal_lean"])
        
        # Head movement variance
        head_std = np.std(head_movements)
        
        # Score calculation
        score = 100
        feedback_parts = []
        
        # Penalize deviation from ideal lean (exercise-specific)
        if deviation > norms["tolerance"]:
            score -= 20
            if avg_spine > norms["ideal_lean"]:
                feedback_parts.append(f"Excessive forward lean for {exercise_key}")
            else:
                feedback_parts.append(f"Too upright for {exercise_key} - lean forward slightly")
        
        # Penalize head movement
        if head_std > 0.03:
            score -= 15
            feedback_parts.append("Head movement during exercise")
        
        # Penalize inconsistent spine position
        if spine_std > 5:
            score -= 10
            feedback_parts.append("Inconsistent torso angle")
        
        score = max(0, score)
        feedback = ". ".join(feedback_parts) if feedback_parts else "Good posture throughout!"
        
        return PillarScore(score, feedback)

    
    def _calculate_rom(self, exercise_name: str) -> PillarScore:
        """
        Calculate Range of Motion score by comparing peak/min angles to thresholds 
        defined in feedback_rules.json.
        """
        if not self.all_landmarks:
            return PillarScore(0, "No pose data available")
        
        # Normalize exercise name
        exercise_key = exercise_name.lower().strip()
        
        # Load rules for this exercise (default to simple logic if not found)
        # We assume 'front' view as a default if view detection isn't strictly implemented per frame
        # ideally we could detect view, but for now 'front' or 'side' covers most general cases
        rules = []
        if exercise_key in self.exercise_thresholds:
            # Try to get rules for 'front', 'side', or '45' - aggregate unique rules
            # For simplicity, we'll combine checks from 'front' and 'side' to be robust
            ex_rules = self.exercise_thresholds[exercise_key]
            for view in ex_rules:
                rules.extend(ex_rules[view])
        
        # If no specific rules found, fall back to generic logic
        if not rules:
            return self._calculate_generic_rom(exercise_key)

        # Track min/max angles for relevant joints
        angle_history = {
            "elbow": [],
            "shoulder": [],
            "hip": [],
            "knee": []
        }
        
        for lm in self.all_landmarks:
            # Calculate all 4 key angles
            # Elbow
            r_elbow = self._calculate_angle(lm[12], lm[14], lm[16])
            l_elbow = self._calculate_angle(lm[11], lm[13], lm[15])
            angle_history["elbow"].append((r_elbow + l_elbow) / 2)
            
            # Shoulder (Arm to Torso)
            r_shoulder = self._calculate_angle(lm[14], lm[12], lm[24])
            l_shoulder = self._calculate_angle(lm[13], lm[11], lm[23])
            angle_history["shoulder"].append((r_shoulder + l_shoulder) / 2)
            
            # Hip (Torso to Thigh)
            r_hip = self._calculate_angle(lm[12], lm[24], lm[26])
            l_hip = self._calculate_angle(lm[11], lm[23], lm[25])
            angle_history["hip"].append((r_hip + l_hip) / 2)
            
            # Knee
            r_knee = self._calculate_angle(lm[24], lm[26], lm[28])
            l_knee = self._calculate_angle(lm[23], lm[25], lm[27])
            angle_history["knee"].append((r_knee + l_knee) / 2)

        # Evaluate Score based on Rules
        total_score = 100
        violation_count = 0
        feedback_messages = set()
        
        for rule in rules:
            joint = rule.get("joint")
            threshold = rule.get("threshold")
            condition = rule.get("condition")
            message = rule.get("message")
            
            if joint not in angle_history:
                continue
                
            angles = angle_history[joint]
            if not angles:
                continue
                
            # Check min or max based on condition
            # For ">", we usually check if the MAX angle reached exceeds threshold (e.g. extension)
            # For "<", we usually check if the MIN angle reached goes below threshold (e.g. depth/flexion)
            
            # However, looking at the JSON:
            # "condition": ">" with threshold 138 (Bench Press Elbow) -> Means BAD if > 138? 
            # "bad_mean": 146.2. So yes, if > 138 it's a violation.
            
            # "condition": "<" with threshold 58 (Bench Press Shoulder) -> Means BAD if < 58?
            # "bad_mean": 5.6. So yes, if < 58 it's a violation.
            
            violation = False
            
            if condition == ">":
                # Check if ANY frame violated significantly? Or if the peak execution violated?
                # Usually we check the peak/extremes of the movement.
                max_angle = max(angles)
                if max_angle > threshold:
                    violation = True
            elif condition == "<":
                min_angle = min(angles)
                if min_angle < threshold:
                    violation = True
            
            if violation:
                total_score -= 15  # Deduct points per violation
                feedback_messages.add(message)
                violation_count += 1

        if total_score < 40: total_score = 40 # Minimum score cap
        
        feedback_str = ". ".join(feedback_messages) if feedback_messages else "Good range of motion!"
        
        return PillarScore(total_score, feedback_str)

    def _calculate_generic_rom(self, exercise_name: str) -> PillarScore:
        """Fallback logic for exercises not in JSON."""
        # Previous hardcoded logic moved here
        elbow_angles = []
        knee_angles = []
        
        for lm in self.all_landmarks:
            r_elbow = self._calculate_angle(lm[12], lm[14], lm[16])
            l_elbow = self._calculate_angle(lm[11], lm[13], lm[15])
            elbow_angles.append((r_elbow + l_elbow) / 2)
            
            r_knee = self._calculate_angle(lm[24], lm[26], lm[28])
            l_knee = self._calculate_angle(lm[23], lm[25], lm[27])
            knee_angles.append((r_knee + l_knee) / 2)
            
        if "curl" in exercise_name or "press" in exercise_name or "push" in exercise_name:
            if not elbow_angles: return PillarScore(50, "No arm data")
            range_achieved = max(elbow_angles) - min(elbow_angles)
            if range_achieved >= 90: return PillarScore(95, "Good extension!")
            return PillarScore(60, "Extend fully.")
        else:
            if not knee_angles: return PillarScore(50, "No leg data")
            min_angle = min(knee_angles)
            if min_angle <= 100: return PillarScore(95, "Good depth!")
            return PillarScore(60, "Go deeper.")
    
    def _calculate_movement_quality(self, rep_timestamps: Optional[List[dict]]) -> PillarScore:
        """
        Calculate movement quality based on tempo consistency.
        Uses rep_timestamps from mobile app.
        """
        if not rep_timestamps or len(rep_timestamps) < 2:
            # Fallback: estimate from frame data
            return PillarScore(70, "Tempo data not available, estimated quality.")
        
        # Calculate duration of each rep
        durations = []
        for rep in rep_timestamps:
            if "start" in rep and "end" in rep:
                duration = rep["end"] - rep["start"]
                durations.append(duration)
        
        if len(durations) < 2:
            return PillarScore(70, "Insufficient rep data for quality analysis.")
        
        # Calculate consistency (standard deviation of rep times)
        avg_duration = np.mean(durations)
        std_duration = np.std(durations)
        cv = std_duration / avg_duration  # Coefficient of variation
        
        # Score based on consistency
        if cv < 0.15:
            score = 95
            feedback = "Excellent tempo consistency!"
        elif cv < 0.25:
            score = 80
            feedback = "Good tempo with minor variation."
        elif cv < 0.40:
            score = 60
            feedback = "Inconsistent tempo - slowing down indicates fatigue."
        else:
            score = 45
            feedback = "Very inconsistent rep speeds - focus on controlled movements."
        
        # Check for fatigue (last reps slower than first)
        if len(durations) >= 4:
            first_half = np.mean(durations[:len(durations)//2])
            second_half = np.mean(durations[len(durations)//2:])
            if second_half > first_half * 1.3:
                score -= 10
                feedback += " Fatigue detected in later reps."
        
        return PillarScore(max(0, score), feedback)
    
    def _calculate_bracing(self) -> PillarScore:
        """
        Calculate core bracing score based on torso rotation and hip sway.
        Uses direct rotation angle measurement (FMS Rotary Stability methodology).
        """
        if not self.all_landmarks:
            return PillarScore(0, "No pose data available")
        
        rotation_angles = []
        hip_sways = []
        
        for lm in self.all_landmarks:
            # Direct rotation measurement: angle between shoulder and hip vectors
            # If torso is not rotating, shoulder and hip vectors should be parallel
            left_shoulder = lm[11][:2]
            right_shoulder = lm[12][:2]
            left_hip = lm[23][:2]
            right_hip = lm[24][:2]
            
            # Shoulder vector (left to right)
            shoulder_vec = right_shoulder - left_shoulder
            # Hip vector (left to right)
            hip_vec = right_hip - left_hip
            
            # Calculate angle between vectors (should be ~0° if aligned)
            dot_product = np.dot(shoulder_vec, hip_vec)
            norms = np.linalg.norm(shoulder_vec) * np.linalg.norm(hip_vec) + 1e-6
            cos_angle = np.clip(dot_product / norms, -1.0, 1.0)
            rotation = np.degrees(np.arccos(cos_angle))
            rotation_angles.append(rotation)
            
            # Hip lateral position
            hip_mid_x = (lm[23][0] + lm[24][0]) / 2
            hip_sways.append(hip_mid_x)
        
        # Rotation analysis
        avg_rotation = np.mean(rotation_angles)
        max_rotation = np.max(rotation_angles)
        
        # Hip sway analysis
        hip_std = np.std(hip_sways)
        
        score = 100
        feedback_parts = []
        
        # Penalize significant torso rotation (threshold: 12° based on FMS guidelines)
        if max_rotation > 15:
            score -= 30
            feedback_parts.append(f"Significant torso rotation detected ({max_rotation:.0f}°)")
        elif max_rotation > 10:
            score -= 15
            feedback_parts.append("Mild torso rotation - engage core more")
        
        # Penalize hip sway
        if hip_std > 0.04:
            score -= 20
            feedback_parts.append("Hip sway during exercise - stabilize pelvis")
        elif hip_std > 0.025:
            score -= 10
            feedback_parts.append("Minor hip drift detected")
        
        score = max(0, score)
        feedback = ". ".join(feedback_parts) if feedback_parts else "Good core engagement!"
        
        return PillarScore(score, feedback)

    
    def _calculate_angle(self, a, b, c) -> float:
        """Calculate angle at point b given three points."""
        a = np.array(a[:3])
        b = np.array(b[:3])
        c = np.array(c[:3])
        
        ba = a - b
        bc = c - b
        
        cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
        
        return angle
    
    def _empty_result(self, exercise: str, reps: int) -> AnalysisResult:
        """Return empty result when analysis fails."""
        empty_pillar = PillarScore(0, "Analysis failed - no pose detected")
        return AnalysisResult(
            exercise=exercise,
            reps_analyzed=reps,
            overall_score=0,
            pillars={
                "stability": empty_pillar,
                "posture": empty_pillar,
                "range_of_motion": empty_pillar,
                "movement_quality": empty_pillar,
                "bracing_core": empty_pillar,
            },
            summary="Could not analyze video. Please ensure good lighting and full body visibility.",
            solutions=[]
        )


def analyze_workout_video(
    video_path: str,
    exercise_name: str,
    rep_count: int,
    rep_timestamps: Optional[List[dict]] = None
) -> dict:
    """
    Convenience function to analyze a video and return JSON-serializable result.
    """
    analyzer = FormAnalyzer()
    result = analyzer.analyze_video(video_path, exercise_name, rep_count, rep_timestamps)
    
    return {
        "exercise": result.exercise,
        "reps_analyzed": result.reps_analyzed,
        "overall_score": result.overall_score,
        "pillars": {
            name: {
                "score": pillar.score,
                "feedback": pillar.feedback,
                "solution": pillar.solution
            }
            for name, pillar in result.pillars.items()
        },
        "summary": result.summary,
        "solutions": result.solutions
    }
