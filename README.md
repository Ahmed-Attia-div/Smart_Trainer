# 🦾 Smart Trainer: Hybrid AI Trainer Coach

Smart Trainer is a state-of-the-art AI coaching ecosystem designed to democratize professional biomechanical analysis. It synergizes **Computer Vision**, **Machine Learning**, and **Sports Science** to provide real-time, expert-level feedback for resistance training.

## 🌟 Key Features

*   **Hybrid Intelligence Architecture**: Combines edge-based deterministic rules for immediate feedback with cloud-based deep analysis.
*   **5-Pillar Biomechanical Engine**: Evaluates every rep based on:
    *   **Stability**: Center of Mass (CoM) variance analysis.
    *   **Posture**: Exercise-specific spinal alignment norms.
    *   **Range of Motion (ROM)**: Topological thresholding for maximum muscle activation.
    *   **Movement Quality**: Tempo consistency and fatigue detection.
    *   **Core Bracing**: Direct torso torsion measurement.
*   **XGBoost Temporal Classifier**: Accurately recognizes 22+ exercises using an 84-dimensional spatiotemporal feature manifold.
*   **AI Coach Advisor**: Integration with OpenAI GPT-4o to provide witty, motivational, and technical correction cues.
*   **Interactive AR Overlay**: Real-time skeletal visualization and auditory feedback loops.

## 📁 Repository Structure

The project is organized into three distinct modules:

*   📂 **`backend/`**: A lightweight FastAPI server optimized for mobile integration (React Native). Processes video uploads and returns 5-pillar scoring via JSON.
*   📂 **`frontend_demo/`**: A full-featured web dashboard for real-time demonstrations, featuring skeletal rendering and voice-over guidance.
*   📂 **`research_lab/`**: Documentation, Jupyter Notebooks for model training, and scientific validation reports.

## 🛠️ Technology Stack

*   **Logic**: Python 3.10+ (FastAPI)
*   **Vision**: MediaPipe BlazePose (3D Landmarks)
*   **ML**: XGBoost (Extreme Gradient Boosting)
*   **LLM**: OpenAI GPT-4o-mini
*   **Frontend**: HTML5, Vanilla JS (Web Speech API, WebSockets)

## 🚦 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
