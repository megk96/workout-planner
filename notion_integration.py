from notion_client import Client
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))
WORKOUTS_DB_ID = os.getenv("NOTION_WORKOUTS_DB_ID")
PLANS_DB_ID = os.getenv("NOTION_PLANS_DB_ID")
STATUS_DB_ID = os.getenv("NOTION_STATUS_DB_ID")

CURRENT_PLAN_PATH = "workout_plans/current_plan.json"

def load_plan_metadata():
    if not os.path.exists(CURRENT_PLAN_PATH):
        raise FileNotFoundError("No current_plan.json found.")
    
    with open(CURRENT_PLAN_PATH, "r") as f:
        data = json.load(f)

    with open(data["metadata_file"], "r") as f:
        metadata = json.load(f)
    return metadata, data["plan_id"]

def update_feedback(video_id, feedback):
    workout_map, plan_id = load_plan_metadata()
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
            "video_id":  {"rich_text": [{"text": {"content": video_id}}]},
            "plan_id":  {"rich_text": [{"text": {"content": plan_id}}]},
        })

    if feedback.get("note"):
        properties["Notes"] = {
            "rich_text": [{"text": {"content": feedback["note"]}}]
        }

    notion.pages.create(parent={"database_id": WORKOUTS_DB_ID}, properties=properties)
    print("✅ Feedback saved to Notion")

    if feedback["status"] == "Completed":
        update_plan_workout_status(plan_id, video_id, "completed")
    elif feedback["status"] in ["Skipped", "Rescheduled"]:
        update_plan_workout_status(plan_id, video_id, "skipped")
    


def create_new_plan_and_set_active(metadata, plan_id, plan_name="Current Plan"):
    from uuid import uuid4

    video_ids = metadata.keys()

    # 1. Set previous active plans to dormant
    previous_active = notion.databases.query(
        database_id=PLANS_DB_ID,
        filter={
            "property": "status",
            "select": {"equals": "active"}
        }
    )
    for result in previous_active["results"]:
        notion.pages.update(
            page_id=result["id"],
            properties={"status": {"select": {"name": "dormant"}}}
        )

    # 2. Create new plan row
    notion.pages.create(
        parent={"database_id": PLANS_DB_ID},
        properties={
            "plan_name": {"title": [{"text": {"content": plan_name}}]},
            "plan_id": {"rich_text": [{"text": {"content": plan_id}}]},
            "video_ids": {"multi_select": [{"name": vid} for vid in video_ids]},
            "status": {"select": {"name": "active"}},
        }
    )

    print(f"✅ Created new plan '{plan_name}' with ID: {plan_id}")
    return plan_id, video_ids


def create_plan_workout_status(plan_id, video_ids, metadata):
    total_days = len(video_ids)

    for vid in video_ids:
        workout = metadata[vid]
        notion.pages.create(
            parent={"database_id": STATUS_DB_ID},
            properties={
                "workout_name": {"title": [{"text": {"content": workout["title"]}}]},
                "plan_id": {"rich_text": [{"text": {"content": plan_id}}]},
                "video_id": {"rich_text": [{"text": {"content": vid}}]},
                "status": {"select": {"name": "queued"}},
                "total_days": {"number": total_days},
                "day_number": {"number": workout["day_number"]},
                "url": {"url": workout["youtube_url"]}
            }
        )
    print(f"✅ Initialized {total_days} entries in PlanWorkoutStatus DB")


def update_plan_workout_status(plan_id, video_id, new_status):
    results = notion.databases.query(
        database_id=STATUS_DB_ID,
        filter={
            "and": [
                {"property": "plan_id", "rich_text": {"equals": plan_id}},
                {"property": "video_id", "rich_text": {"equals": video_id}},
            ]
        }
    )

    if not results["results"]:
        raise ValueError(f"No PlanWorkoutStatus found for plan {plan_id} and video {video_id}")

    page_id = results["results"][0]["id"]

    props = {
        "status": {"select": {"name": new_status}},
    }

    if new_status == "sent":
        props["sent_at"] = {"date": {"start": datetime.utcnow().isoformat()}}

    notion.pages.update(
        page_id=page_id,
        properties=props
    )

    print(f"📬 Marked video {video_id} as '{new_status}' in PlanWorkoutStatus")
