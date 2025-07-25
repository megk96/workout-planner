import json
import os
from datetime import datetime
from uuid import uuid4
from yt_dlp import YoutubeDL

from notion_integration import create_new_plan_and_set_active, create_plan_workout_status

WORKOUT_TXT = "workout_plans/current_plan.txt"
PLAN_DIR = "workout_plans"
CURRENT_JSON = os.path.join(PLAN_DIR, "current_plan.json")
GLOBAL_METADATA_PATH = os.path.join(PLAN_DIR, "metadata.json")

YDL_OPTIONS = {
    'quiet': True,
    'skip_download': True,
    'extract_flat': False,
    'forcejson': True,
}

def extract_metadata(url):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "youtube_url": url,
            "video_id": info.get("id"),
            "duration": round(info.get("duration") / 60),
            "description": info.get("description", "").split("\n")[0],
            "type": "Yoga" if "yoga" in info.get("title", "").lower() else "Strength",
        }

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    else:
        raise ValueError(f"Invalid YouTube URL: {url}")

def main():
    # Load URLs
    with open(WORKOUT_TXT, "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    # Load global metadata
    if os.path.exists(GLOBAL_METADATA_PATH):
        with open(GLOBAL_METADATA_PATH, "r") as f:
            global_metadata = json.load(f)
    else:
        global_metadata = {}

    current_metadata = {}
    updated = False

    for idx, url in enumerate(urls):
        video_id = extract_video_id(url)
        if video_id in global_metadata:
            print(f"✅ Cached: {video_id}")
            video = global_metadata[video_id]
        else:
            print(f"🔍 Fetching new metadata: {url}")
            video = extract_metadata(url)
            global_metadata[video_id] = video
            updated = True

        video["day_number"] = idx+1
        current_metadata[video_id] = video

    # Update global metadata if needed
    if updated:
        with open(GLOBAL_METADATA_PATH, "w") as out:
            json.dump(global_metadata, out, indent=2)
            print("📁 Global metadata updated")

    # Save plan-specific metadata
    plan_id = "plan_" + str(uuid4())[:8]
    metadata_file = os.path.join(PLAN_DIR, f"{plan_id}_metadata.json")
    with open(metadata_file, "w") as out:
        json.dump(current_metadata, out, indent=2)
        print(f"✅ Plan metadata saved to {metadata_file}")

    # Create new plan in Notion
    plan_name = "Plan - " + datetime.today().strftime("%Y-%m-%d")
    actual_plan_id, video_ids = create_new_plan_and_set_active(current_metadata, plan_id, plan_name)

    # Save current plan pointer
    with open(CURRENT_JSON, "w") as out:
        json.dump({
            "plan_id": actual_plan_id,
            "video_ids": list(video_ids),
            "metadata_file": metadata_file
        }, out, indent=2)
        print("📌 current_plan.json updated.")

    # Initialize PlanWorkoutStatus
    create_plan_workout_status(actual_plan_id, video_ids, current_metadata)

if __name__ == "__main__":
    main()
