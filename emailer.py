import os
import requests
from dotenv import load_dotenv

from email_utils import load_today_workout
from llm import compose_email
from notion_integration import update_plan_workout_status
import json

env = os.getenv("ENVIRONMENT", "dev").upper()

load_dotenv()

RESEND_API_KEY = os.getenv(f"RESEND_API_KEY_{env}") 
SENDER_EMAIL = os.getenv("SENDER_EMAIL") 
RECEIVER_EMAIL = os.getenv(f"RECEIVER_EMAIL_{env}")
FEEDBACK_URL_BASE = os.getenv(f"FEEDBACK_URL_BASE_{env}")

def send_email(recipient, subject, body, youtube_url=None, video_id=None):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    # Get YouTube thumbnail
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg" if video_id else ""
    feedback_url = f"{FEEDBACK_URL_BASE}/?video_id={video_id}"
    html_safe_body = body.replace('\n', '<br>')

    html_body = f"""
    <html>
    <body style="font-family: sans-serif; line-height: 1.5; color: #222;">

        <p style="margin-bottom: 20px;">
            ✅ When you're done, let me know how it went:<br>
            <a href="{feedback_url}" style="background-color: #4CAF50; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 8px;">
                Submit Feedback
            </a>
        </p>

        <p>{html_safe_body}</p>

        <a href="{youtube_url}" target="_blank">
            <img src="{thumbnail_url}" alt="Watch workout" width="480" style="border-radius: 8px; margin-top: 12px;">
        </a>

    </body>
    </html>
    """


    payload = {
        "from": SENDER_EMAIL,
        "to": [recipient],
        "subject": subject,
        "html": html_body,
        "text": body  # fallback
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        print(f"✅ Email sent to {recipient}")
        try:
            with open("workout_plans/current_plan.json") as f:
                plan_data = json.load(f)
            plan_id = plan_data["plan_id"]
            video_id = workout["video_id"]
            update_plan_workout_status(plan_id, video_id, "sent")
        except Exception as e:
            print(f"❌ Status sent updation failed: {e}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


if __name__ == "__main__":
    workout = load_today_workout()
    email = compose_email(workout)
    send_email(
            recipient=RECEIVER_EMAIL,
            subject=email["subject"],
            body=email["body"],
            youtube_url=workout["youtube_url"],
            video_id=workout["video_id"]
        )
    
