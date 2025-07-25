import json
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))
STATUS_DB_ID = os.getenv("NOTION_STATUS_DB_ID")

CURRENT_PLAN_FILE = "workout_plans/current_plan.json"

class NoWorkoutFoundError(Exception):
    pass

def load_today_workout():
    # 1. Load current plan pointer
    with open(CURRENT_PLAN_FILE) as f:
        plan_data = json.load(f)

    plan_id = plan_data["plan_id"]
    metadata_file = plan_data["metadata_file"]

    # 2. Load metadata
    with open(metadata_file) as f:
        metadata = json.load(f)

    # 3. Query Notion for PlanWorkoutStatus
    results = notion.databases.query(
        database_id=STATUS_DB_ID,
        filter={
            "property": "plan_id",
            "rich_text": {"equals": plan_id}
        },
        sorts=[{"property": "day_number", "direction": "ascending"}]
    )["results"]

    for preferred_status in ["queued", "sent", "skipped"]:
        for row in results:
            props = row["properties"]
            if props["status"]["select"]["name"] == preferred_status:
                video_id = props["video_id"]["rich_text"][0]["text"]["content"]
                if video_id in metadata:
                    return metadata[video_id]
                else:
                    raise ValueError(f"❌ Metadata for video_id {video_id} not found.")
    
    raise NoWorkoutFoundError("❌ No queued or sent workouts found. Please set a new plan.")
