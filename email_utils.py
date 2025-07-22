import json

WORKOUT_METADATA_FILE = "workout_plans/current_plan_metadata.json"

def load_today_workout():
    with open(WORKOUT_METADATA_FILE) as f:
        workouts = json.load(f)
    return workouts[0]  # Always use the first workout
