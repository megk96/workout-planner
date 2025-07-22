from notion_client import Client
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))
DB_ID = os.getenv("NOTION_DB_ID")

def load_plan():
    with open("workout_plans/current_plan_metadata.json") as f:
        workouts = json.load(f)
    return {w["video_id"]: w for w in workouts}

def update_feedback(video_id, feedback):
    workout_map = load_plan()
    workout = workout_map.get(video_id)

    if not workout:
        print(f"❌ Workout {video_id} not found in local JSON")
        raise ValueError("Workout not found")

    properties = {
        "Name": {"title": [{"text": {"content": workout["title"]}}]},
        "Date": {"date": {"start": datetime.today().isoformat()}},
        "Duration": {"number": workout["duration"]},
        "URL": {"url": workout["youtube_url"]},
        "Summary": {"rich_text": [{"text": {"content": workout["description"]}}]},
        "Status": {"select": {"name": feedback["status"]}},
    }

    if feedback["status"] == "Completed":
        properties.update({
            "Effort Level": {"number": feedback["effort"]},
            "Effectiveness": {"number": feedback["effectiveness"]},
            "Mood": {"multi_select": [{"name": m} for m in feedback.get("mood", [])]},
            "Type": {"multi_select": [{"name": t} for t in feedback.get("types", [])]},
            "Muscles Weak": {"multi_select": [{"name": m} for m in feedback.get("muscles_weak", [])]},
        })

    if feedback.get("note"):
        properties["Notes"] = {
            "rich_text": [{"text": {"content": feedback["note"]}}]
        }

    notion.pages.create(parent={"database_id": DB_ID}, properties=properties)
    print("✅ Feedback saved to Notion")