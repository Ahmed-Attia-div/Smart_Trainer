"""
AI Advisor Module - Generates workout feedback using OpenAI GPT
"""
import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


def get_ai_feedback(exercise_name: str, pillar_scores: dict, rep_count: int) -> str:
    """
    Generate personalized workout feedback using OpenAI GPT.
    
    Args:
        exercise_name: Name of the exercise (e.g., "Bicep Curl")
        pillar_scores: Dictionary with scores for each pillar
        rep_count: Total number of reps performed
    
    Returns:
        AI-generated feedback text (witty and motivational)
    """
    if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        # Fallback if no API key configured
        return _generate_template_feedback(pillar_scores)
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Build the analysis summary for the prompt
    issues = []
    strengths = []
    
    for pillar, data in pillar_scores.items():
        score = data.get("score", 0)
        feedback = data.get("feedback", "")
        
        if score < 70:
            issues.append(f"{pillar}: {feedback} (Score: {score}/100)")
        elif score >= 85:
            strengths.append(f"{pillar}: {feedback} (Score: {score}/100)")
    
    prompt = f"""You are a tough but funny gym coach giving feedback after a workout.

Exercise: {exercise_name}
Total Reps: {rep_count}

ISSUES DETECTED:
{chr(10).join(issues) if issues else "None - Great form!"}

STRENGTHS:
{chr(10).join(strengths) if strengths else "Room for improvement in all areas."}

Write a SHORT (2-3 sentences max) witty critique that:
1. Uses a funny metaphor or comparison
2. Acknowledges what they did well (if any)
3. Points out the main issue to fix

Then provide 2 BRIEF technical solutions (1 sentence each).

Format your response as JSON:
{{
  "summary": "Your witty critique here...",
  "solutions": ["Solution 1...", "Solution 2..."]
}}
"""
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a fitness coach who gives brief, witty feedback. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON response
        try:
            parsed = json.loads(result)
            return parsed
        except json.JSONDecodeError:
            # If not valid JSON, return as plain text
            return {"summary": result, "solutions": []}
            
    except Exception as e:
        print(f"[AI ADVISOR ERROR] {e}")
        return _generate_template_feedback(pillar_scores)


def _generate_template_feedback(pillar_scores: dict) -> dict:
    """
    Fallback template-based feedback when OpenAI is not available.
    """
    # Find the worst pillar
    worst_pillar = min(pillar_scores.items(), key=lambda x: x[1].get("score", 100))
    pillar_name = worst_pillar[0]
    pillar_data = worst_pillar[1]
    
    templates = {
        "stability": {
            "summary": "You're wobbling more than a shopping cart with a broken wheel. Plant those feet!",
            "solutions": [
                "Grip the floor with your toes and distribute weight evenly.",
                "Engage your glutes before starting each rep."
            ]
        },
        "posture": {
            "summary": "Your head is moving around like you're watching a tennis match. Eyes forward, champ!",
            "solutions": [
                "Pick a spot on the wall and stare at it throughout the set.",
                "Keep your chin tucked and spine neutral."
            ]
        },
        "rom": {
            "summary": "Those reps are shorter than a TikTok video. Go deeper!",
            "solutions": [
                "Focus on full range of motion, even if it means lighter weight.",
                "Pause at the bottom of each rep to ensure full stretch."
            ]
        },
        "movement_quality": {
            "summary": "Your tempo is all over the place - fast, slow, fast. Pick a rhythm and stick to it!",
            "solutions": [
                "Count 2 seconds down, 1 second up for each rep.",
                "Rest longer between sets if fatigue is affecting your control."
            ]
        },
        "bracing": {
            "summary": "Your core has the stability of a wet noodle. Brace like someone's about to punch you!",
            "solutions": [
                "Take a deep breath and tighten your abs before each rep.",
                "Imagine pulling your belly button toward your spine."
            ]
        }
    }
    
    return templates.get(pillar_name, {
        "summary": "Good effort! Keep working on your form.",
        "solutions": ["Focus on controlled movements.", "Record yourself to spot issues."]
    })
