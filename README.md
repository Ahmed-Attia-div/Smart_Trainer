# BioMotion Core - Biometric Analytics & Backend

> **The Brain Behind the App:** A high-performance FastAPI microservice handling Computer Vision, Biomechanics Analysis, and Expert Coaching for the GymScore Full Stack System.

---

## 🏗️ The Full Stack Architecture

This project serves as the **Backend API** and **Computational Processing Unit** for the GymScore ecosystem. It is designed to interpret both live workout data and recorded video files.

```mermaid
graph TD
    User[Mobile App User] <-->|Live Stream / Upload| Frontend[React Native App]
    Frontend <-->|Process Request| Backend[**FastAPI Backend** (This Repo)]
    Backend -->|Pose Estimation| MediaPipe[MediaPipe Engine]
    Backend -->|Cognitive Feedback| LLM[Large Language Model]
    Backend -->|Analysis JSON| Frontend
```

---

## 🧠 Core Strategy: Post-Workout Video Analytics

The system is built on a unified **"Video-to-Insight"** pipeline. Whether the input is a pre-recorded file or a live camera stream, the backend treats every interaction as a "Workout Session" that requires high-fidelity analysis.

### Unified Processing Pipeline
*   **Biomechanical Analysis**: Extracts 33 skeleton landmarks from every frame to measure joint angles and body positioning.
*   **5-Pillar Evaluation**: Applies physics-based rules to calculate scores for Stability, Posture, ROM, Movement Quality, and Bracing.
*   **Expert Coaching**: Translates raw data into personalized, witty, and actionable feedback via sophisticated language processing.

### Flexible Input Methods
1.  **Recorded Upload**: For analyzing historical workouts. The app sends a full video file for retrospective analysis.
2.  **Live Streaming**: For real-time sessions. The app streams frames via WebSockets, allowing the backend to provide immediate cues before final evaluation.


---

## 🧠 The Expert Logic Engine

### The "Witty Coach" Persona (LLM Integration)
The system uses automated language processing to turn raw biomechanical data into human-like coaching:
*   *Input:* "Knee instability detected (Variance: 0.08), Depth: 110 deg."
*   *Output:* "Your squats are deep, but you're wobbling like a jelly on a washing machine. Tighten that core!"

### 5-Pillar Scoring System
Every workout is evaluated on:
1.  **Stability**: Body control and balance.
2.  **Posture**: Spinal alignment and head position.
3.  **Range of Motion (ROM)**: Depth and extension quality.
4.  **Movement Quality**: Tempo consistency and fatigue detection.
5.  **Bracing**: Core engagement and stiffness.

---

## 📡 API Documentation

### 🟢 Post-Workout Video Analytics
The core engine of this backend is designed for high-fidelity biomechanical analysis. Whether the video is uploaded as a file or streamed frame-by-frame, the backend treats all inputs as a **"Workout Session"** to generate the same comprehensive 5-pillar report.

#### Core Analysis Pipeline:
1.  **Biomechanical Processing:** Extracts pose landmarks (33 points) from the video stream.
2.  **5-Pillar Evaluation:** Calculates scores for **Stability, Posture, ROM, Movement Quality, and Bracing**.
3.  **Expert Coaching:** Generates human-like summaries and actionable solutions using computational linguistics.

#### Input Methods (Integration):
*   **File Upload (`POST /api/analyze-form`):** Used for pre-recorded videos. The app sends the video file along with exercise metadata.
*   **Real-Time Stream (`WS /ws/{session_id}`):** Used during live sessions. The app streams frames, and the backend provides immediate cues while accumulating data for the final report.

**Final Result:** A unified JSON response containing overall scores, pillar breakdowns, and personalized expert feedback.

---



## 🛠️ Technology Stack

| Component | Technology | Why? |
|-----------|------------|------|
| **Web Framework** | **FastAPI** | Fastest Python framework, auto-docs (Swagger). |
| **Vision Model** | **MediaPipe Landmarker** | Efficient, privacy-first pose estimation. |
| **Video Processing** | **OpenCV** | Robust frame extraction. |
| **Expert Logic** | **GPT-4o** | Dynamic, non-robotic feedback text. |
| **ML Models** | **XGBoost / CNN** | For exercise verification and integrity checks. |

---

## ⚡ How to Run

### Prerequisites
*   Python 3.9+
*   Environment Key Configuration

### Installation

1.  **Clone & Install Dependencies**
    ```bash
    git clone <repo_url>
    cd trainer-backend
    python -m venv venv
    venv\Scripts\activate      # Windows
    pip install -r requirements.txt
    ```

2.  **Configure API Keys**
    *   Open `config.py`.
    *   Set the necessary API credentials.

3.  **Run the Server**
    ```bash
    python run_server.py
    ```
    *   Server runs on: `http://0.0.0.0:8000`
    *   Interactive Docs: `http://localhost:8000/docs`

---

## 📂 Project Structure

```
trainer-backend/
├── api_server.py           # 🚀 Application Entry Point
├── form_analyzer.py        # 🧠 Biomechanics Engine (Scoring Logic)
├── ai_advisor.py           # 🤖 Expert Interface
├── exercise_detector.py    # 🕵️ Exercise Verification Logic
├── count_reps.py           # 🔢 Rep Counting Logic
├── config.py               # 🔑 Configuration
├── requirements.txt        # 📦 Dependencies
└── pose_landmarker.task    # 🦴 MediaPipe Model
```

---
> **Deployment Note:** This backend is stateless and container-ready.
