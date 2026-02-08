"""
Calorie Calculator Module
=========================
Estimates calories burned based on exercise, reps, and user weight.

Formula: Calories = MET * weight_kg * duration_hours
Where duration is estimated from reps and exercise type.
"""

# قيم MET (Metabolic Equivalent of Task) لكل تمرين
# المصدر: Compendium of Physical Activities
MET_VALUES = {
    # Upper Body - Moderate
    "barbell biceps curl": 3.5,
    "hammer curl": 3.5,
    "tricep pushdown": 3.5,
    "tricep dips": 4.0,
    "lateral raises": 3.5,
    
    # Upper Body - Heavy
    "bench press": 5.0,
    "incline bench press": 5.0,
    "decline bench press": 5.0,
    "shoulder press": 5.0,
    "chest fly machine": 4.0,
    
    # Back - Heavy
    "lat pulldown": 5.5,
    "pull up": 8.0,
    "t bar row": 6.0,
    
    # Legs - Heavy
    "squat": 6.0,
    "deadlift": 6.0,
    "romanian deadlift": 5.5,
    "hip thrust": 5.0,
    "leg extension": 4.0,
    "leg raises": 4.5,
    
    # Core
    "push up": 4.0,
    "plank": 3.0,
    "russian twist": 4.0,
}

# متوسط الوقت لكل عدة (بالثواني)
SECONDS_PER_REP = {
    "barbell biceps curl": 3,
    "hammer curl": 3,
    "bench press": 4,
    "incline bench press": 4,
    "decline bench press": 4,
    "chest fly machine": 3,
    "shoulder press": 4,
    "lateral raises": 3,
    "lat pulldown": 3,
    "pull up": 4,
    "t bar row": 3,
    "tricep dips": 3,
    "tricep pushdown": 2,
    "push up": 2,
    "plank": 1,  # per second
    "squat": 4,
    "deadlift": 5,
    "romanian deadlift": 4,
    "hip thrust": 3,
    "leg extension": 3,
    "leg raises": 3,
    "russian twist": 2,
}

# الوزن الافتراضي (كجم) - يمكن تغييره من الإعدادات
DEFAULT_WEIGHT_KG = 70


class CalorieTracker:
    """Tracks calories burned during workout session."""
    
    def __init__(self, weight_kg: float = DEFAULT_WEIGHT_KG):
        self.weight_kg = weight_kg
        self.total_calories = 0.0
        self.exercise_calories = {}  # calories per exercise
        self.exercise_reps = {}      # reps per exercise
    
    def add_reps(self, exercise_name: str, reps: int) -> float:
        """
        Add reps and calculate calories burned.
        
        Args:
            exercise_name: Name of exercise
            reps: Number of reps completed
            
        Returns:
            Calories burned for this batch of reps
        """
        exercise_lower = exercise_name.lower()
        
        met = MET_VALUES.get(exercise_lower, 4.0)  # default MET
        secs_per_rep = SECONDS_PER_REP.get(exercise_lower, 3)
        
        # حساب المدة بالساعات
        duration_hours = (reps * secs_per_rep) / 3600
        
        # حساب السعرات
        calories = met * self.weight_kg * duration_hours
        
        # تحديث التتبع
        self.total_calories += calories
        
        if exercise_lower not in self.exercise_calories:
            self.exercise_calories[exercise_lower] = 0.0
            self.exercise_reps[exercise_lower] = 0
        
        self.exercise_calories[exercise_lower] += calories
        self.exercise_reps[exercise_lower] += reps
        
        return calories
    
    def get_total_calories(self) -> float:
        """Get total calories burned."""
        return round(self.total_calories, 1)
    
    def get_summary(self) -> dict:
        """Get detailed calorie summary."""
        return {
            "total": round(self.total_calories, 1),
            "by_exercise": {
                ex: {
                    "calories": round(cal, 1),
                    "reps": self.exercise_reps[ex]
                }
                for ex, cal in self.exercise_calories.items()
            }
        }
    
    def reset(self):
        """Reset tracker for new session."""
        self.total_calories = 0.0
        self.exercise_calories = {}
        self.exercise_reps = {}


def estimate_calories(exercise_name: str, reps: int, weight_kg: float = DEFAULT_WEIGHT_KG) -> float:
    """
    Quick function to estimate calories for a given exercise.
    
    Args:
        exercise_name: Name of exercise
        reps: Number of reps
        weight_kg: User's weight in kg
        
    Returns:
        Estimated calories burned
    """
    exercise_lower = exercise_name.lower()
    
    met = MET_VALUES.get(exercise_lower, 4.0)
    secs_per_rep = SECONDS_PER_REP.get(exercise_lower, 3)
    
    duration_hours = (reps * secs_per_rep) / 3600
    calories = met * weight_kg * duration_hours
    
    return round(calories, 2)


def format_calories_text(calories: float) -> str:
    """Format calories for display."""
    if calories < 1:
        return f"🔥 {calories:.1f} cal"
    return f"🔥 {calories:.0f} cal"


# للتجربة
if __name__ == "__main__":
    tracker = CalorieTracker(weight_kg=75)
    
    # Simulate workout
    tracker.add_reps("squat", 10)
    tracker.add_reps("squat", 10)
    tracker.add_reps("bench press", 10)
    tracker.add_reps("pull up", 8)
    
    summary = tracker.get_summary()
    print(f"Total Calories: {summary['total']} cal")
    print("\nBy Exercise:")
    for ex, data in summary["by_exercise"].items():
        print(f"  {ex}: {data['reps']} reps → {data['calories']} cal")
