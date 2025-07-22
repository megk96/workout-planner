from flask import Flask, request, render_template
from notion_integration import update_feedback

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        feedback_data = {
            "video_id": request.form["video_id"],
            "mood": request.form.get("mood", "").split(",") if request.form.get("mood") else [],
            "effort": int(request.form.get("effort", 5)),
            "energy": int(request.form.get("energy", 5)),
            "note": request.form.get("note", "").strip(),
            "status": request.form.get("status", "Completed"),
        }
        try:
            update_feedback(feedback_data["video_id"], feedback_data)
            return "✅ Feedback submitted. Notion updated."
        except ValueError as e:
            return f"❌ Error: {str(e)}"
        except Exception:
            return "❌ An unexpected error occurred while saving feedback."

    # GET method: retrieve video_id from query string
    video_id = request.args.get("video_id", "")
    return render_template("feedback.html", video_id=video_id)
