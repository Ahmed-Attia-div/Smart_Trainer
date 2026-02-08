from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import tempfile
import json
from form_analyzer import analyze_workout_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "BioMotion Core Backend Running"}

# ============================================================
# POST-WORKOUT ANALYSIS ENDPOINT (Mobile App Only)
# ============================================================

@app.post("/api/analyze-form")
async def analyze_form(
    video: UploadFile = File(...),
    exercise_name: str = Form(...),
    rep_count: int = Form(...),
    rep_timestamps: str = Form(None)  # JSON string
):
    """
    Analyze a workout video and return 5-pillar form scoring.
    """
    print(f"[ANALYZE-FORM] Received: {exercise_name}, {rep_count} reps")
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"workout_{uuid.uuid4()}.mp4")
    
    try:
        with open(temp_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        timestamps = None
        if rep_timestamps:
            try:
                timestamps = json.loads(rep_timestamps)
            except json.JSONDecodeError:
                timestamps = None
        
        result = analyze_workout_video(
            video_path=temp_path,
            exercise_name=exercise_name,
            rep_count=rep_count,
            rep_timestamps=timestamps
        )
        
        return result
        
    except Exception as e:
        print(f"[ANALYZE-FORM ERROR] {e}")
        return {
            "error": str(e),
            "exercise": exercise_name,
            "overall_score": 0,
            "pillars": {},
            "summary": "Analysis failed. Please try again.",
            "solutions": []
        }
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
