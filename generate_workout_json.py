import json
from yt_dlp import YoutubeDL

WORKOUT_FILE = "workout_plans/current_plan.txt"
WORKOUT_METADATA_FILE = "workout_plans/current_plan_metadata.json"
# Basic options for metadata-only extraction
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
            "duration": round(info.get("duration") / 60),  # convert to minutes
            "description": info.get("description", "").split("\n")[0],  # first line
        }

def main():
    workout_entries = []
    with open(WORKOUT_FILE, "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    for idx, url in enumerate(urls):
        print(f"Fetching metadata for Day {idx+1}: {url}")
        metadata = extract_metadata(url)
        workout_entry = {
            "day_number": idx + 1,
            "title": metadata["title"],
            "youtube_url": metadata["youtube_url"],
            "video_id": metadata["video_id"],
            "duration": metadata["duration"],
            "description": metadata["description"],
            "type": "Yoga" if "yoga" in metadata["title"].lower() else "Strength",
            "intensity": "Low",
            "equipment": "None"
        }
        workout_entries.append(workout_entry)

    with open(WORKOUT_METADATA_FILE, "w") as out_file:
        json.dump(workout_entries, out_file, indent=2)
        print("✅ workouts.json generated!")

if __name__ == "__main__":
    main()
